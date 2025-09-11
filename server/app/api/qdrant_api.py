from fastapi import APIRouter, Request
from app.api.models import PromptRequest
from app.service.llm_services import generate_offline, generate_online

qdrant_router = APIRouter()


@qdrant_router.post("/generate")
async def generate_text(req: Request, request: PromptRequest):
    """
    Generates a text response using either an online (Gemini) or offline (Ollama) model.
    The prompt is augmented with context from a Qdrant vector database.
    """
    prompt = request.prompt.strip()
    mode = request.mode.lower()
    project = request.project
    template = request.template.lower()

    # Augment the prompt with RAG
    qdrant_manager = req.app.state.qdrant_manager
    augmented_prompt = qdrant_manager.augment_prompt(prompt, project, template)
    print(f"Augmented Prompt: {augmented_prompt}")

    if mode == "online":
        return await generate_online(augmented_prompt)
    else:
        return await generate_offline(augmented_prompt)
