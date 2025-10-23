from fastapi import APIRouter, Request
from app.api.models import PromptRequest
from app.service.llm_services import generate_offline, generate_online
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Literal
prompt_router = APIRouter()


@prompt_router.post("/generate/")
async def generate_text(request: Request, payload: PromptRequest):
    """
    Generates a text response using either an online (Gemini) or offline (Ollama) model.
    The prompt is augmented with context from a Qdrant vector database.
    """
    prompt = payload.prompt.strip()
    mode = payload.mode.lower()
    project_id = payload.project
    template = payload.template.lower()

    # Augment the prompt with RAG
    qdrant_manager = request.app.state.qdrant_manager
    augmented_prompt = qdrant_manager.augment_prompt(prompt, project_id, template)
    print(f"Augmented Prompt: {augmented_prompt}")

    if mode == "online":
        return await generate_online(augmented_prompt)
    else:
        return await generate_offline(augmented_prompt)
    


prompt_router = APIRouter(prefix="/prompt", tags=["Prompt"])

# app/api/prompt_endpoints.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field  # <-- Field imported here
from typing import List, Literal

# Try to use your real LLM services; fall back to safe stubs if unavailable
try:
    from app.llm_services import generate_offline, generate_online
except Exception:
    def generate_offline(prompt: str) -> str:
        return "⚠️ LLM (offline) not wired. Prompt was:\n" + prompt[:2000]
    def generate_online(prompt: str) -> str:
        return "⚠️ LLM (online) not wired. Prompt was:\n" + prompt[:2000]

# Use your existing DB stores (same module used in main.py)
from app.database import Highlight as HighlightStore, Transcription as TranscriptionStore

prompt_router = APIRouter(prefix="/prompt", tags=["Prompt"])

class AskHighlightsRequest(BaseModel):
    transcription_id: int
    colors: List[str] = Field(default_factory=list)   # e.g. ["orange","yellow"]
    question: str
    mode: Literal["offline", "online"] = "offline"    # offline=Ollama CPU, online=Gemini

@prompt_router.post("/ask_highlights")
def ask_highlights(req: Request, payload: AskHighlightsRequest):
    """
    Answer using ONLY text from highlights (optionally filtered by color).
    """

    # --- Fetch transcription text ---
    try:
        t = TranscriptionStore(req.app.state.transcripts_store.db_name)
        if hasattr(t, "get_transcription_by_id"):
            _proj_id, _name, full_text, _created = t.get_transcription_by_id(payload.transcription_id)
        elif hasattr(t, "get_by_id"):
            rec = t.get_by_id(payload.transcription_id)
            full_text = rec.get("transcription") or rec.get("text") or ""
        else:
            raise LookupError("Transcription store missing 'get_transcription_by_id'/'get_by_id'")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Transcription not found: {e}")

    # --- Fetch highlights for this transcription ---
    try:
        hs = HighlightStore(req.app.state.transcripts_store.db_name)
        if hasattr(hs, "get_all_for_transcription"):
            all_hls = hs.get_all_for_transcription(payload.transcription_id)
        elif hasattr(hs, "list_by_transcription"):
            all_hls = hs.list_by_transcription(payload.transcription_id)
        else:
            raise LookupError("Highlight store missing 'get_all_for_transcription'/'list_by_transcription'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read highlights: {e}")

    # --- Filter by color (if provided) ---
    if payload.colors:
        wanted = set(payload.colors)
        filtered = [h for h in all_hls if (h.get("color") in wanted)]
    else:
        filtered = all_hls

    if not filtered:
        return {"answer": "I couldn’t find any highlights for the selected colours.", "used_context": []}

    # --- Normalize & merge overlapping ranges ---
    def s_of(h): return h.get("startOffset", h.get("start", h.get("start_idx", 0)))
    def e_of(h): return h.get("endOffset",   h.get("end",   h.get("end_idx",   0)))
    def c_of(h): return h.get("color", "yellow")

    norm = [{"start": int(s_of(h)), "end": int(e_of(h)), "color": c_of(h)} for h in filtered]
    norm.sort(key=lambda r: (r["start"], r["end"]))

    merged: List[dict] = []
    for r in norm:
        if not merged or r["start"] > merged[-1]["end"]:
            merged.append(r.copy())
        else:
            merged[-1]["end"] = max(merged[-1]["end"], r["end"])  # simple merge; keeps first color

    # --- Slice text for context ---
    contexts = []
    L = len(full_text or "")
    for r in merged:
        s = max(0, min(r["start"], L))
        e = max(0, min(r["end"],   L))
        if e > s:
            contexts.append({
                "range": [s, e],
                "color": r["color"],
                "text": (full_text[s:e].strip()),
            })

    if not contexts:
        return {"answer": "No usable text found in the selected highlight ranges.", "used_context": []}

    # --- Build grounded prompt ---
    context_block = "\n\n".join(f"[{c['color']}] {c['text']}" for c in contexts if c["text"])
    user_msg = (
        "You are an assistant that MUST answer only from the provided quotes.\n"
        "If the answer cannot be found there, say so explicitly.\n\n"
        f"QUESTION:\n{payload.question}\n\n"
        f"=== HIGHLIGHT QUOTES ===\n{context_block}\n"
    )

    # --- Call LLM ---
    try:
        if payload.mode == "offline":
            answer = generate_offline(user_msg)   # Ollama (CPU)
        else:
            answer = generate_online(user_msg)    # Gemini
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    return {"answer": answer, "used_context": contexts, "meta": {"mode": payload.mode, "colors": payload.colors}}
