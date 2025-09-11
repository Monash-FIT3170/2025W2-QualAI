from fastapi import APIRouter, Request
from app.api.models import PromptRequest
from app.service.llm_services import generate_offline, generate_online

prompt_router = APIRouter()


@prompt_router.post("/generate")
async def generate_text(request: Request, payload: PromptRequest):
    """
    Generates a text response using either an online (Gemini) or offline (Ollama) model.
    The prompt is augmented with context from a Qdrant vector database.
    """
    prompt = payload.prompt.strip()
    mode = payload.mode.lower()
    project_name = payload.project
    template = payload.template.lower()

    # Augment the prompt with RAG
    qdrant_manager = request.app.state.qdrant_manager
    augmented_prompt = qdrant_manager.augment_prompt(prompt, project_name, template)
    print(f"Augmented Prompt: {augmented_prompt}")

    if mode == "online":
        return await generate_online(augmented_prompt)
    else:
        return await generate_offline(augmented_prompt)
