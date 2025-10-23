from fastapi import APIRouter, Request
from app.api.models import PromptRequest
from app.service.llm_services import generate_offline, generate_online

prompt_router = APIRouter()


@prompt_router.post("/generate")
async def generate_text(request: Request, payload: PromptRequest):
    """
    Generates a text response using either an online (Gemini) or offline (Ollama) model.
    The prompt is augmented with context from a Qdrant vector database.
    The AI response is saved to the project's chat history.
    """
    prompt = payload.prompt.strip()
    mode = payload.mode.lower()
    project_id = payload.project
    template = payload.template.lower()

    # Augment the prompt with RAG
    qdrant_manager = request.app.state.qdrant_manager
    augmented_prompt = qdrant_manager.augment_prompt(
        prompt, project_id, template)
    print(f"Augmented Prompt: {augmented_prompt}")

    # Generate AI response
    if mode == "online":
        result = await generate_online(augmented_prompt)
    else:
        result = await generate_offline(augmented_prompt)

    # Save AI response to database (backend is responsible for saving)
    ai_response = result.get("response", "")
    if ai_response and project_id:
        try:
            request.app.state.chat_history_store.insert(
                project_id=project_id, sender="ai", message=ai_response
            )
            print(f"Saved AI response to project {project_id}")
        except Exception as e:
            print(f"Failed to save AI response: {e}")
            # Don't fail the request if save fails

    return result
