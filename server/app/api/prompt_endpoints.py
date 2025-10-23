from fastapi import APIRouter, Request
from app.api.models import PromptRequest
from app.service.llm_services import generate_offline, generate_online

from app.database.Codes import Codes
from app.config import config
import re


prompt_router = APIRouter()


@prompt_router.post("/generate")
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
    
@prompt_router.post("/generate_code")
async def generate_codes(request: Request, payload: PromptRequest):
    """
    Generates the codes using either an online (Gemini) or offline (Ollama) model.
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
        promptResponse = await generate_online(augmented_prompt)
        print(promptResponse)
        #return promptResponse
    else:
        promptResponse = await generate_offline(augmented_prompt)
        #return promptResponse
    


    promptResponseText = promptResponse["response"]
    codes = extract_text(promptResponseText)
    print(codes)

    codesDatabase = Codes(config.DB_PATH)
    
    existing_codes = {name for _, name, _, _ in codesDatabase.get_all_codes()}

    #insert or update code based on database storage
    for code_name, quotes in codes.items():
        if code_name in existing_codes:
            # update existing code instead
            code_id = next(c[0] for c in codesDatabase.get_all_codes() if c[1] == code_name)
            codesDatabase.update(code_id, code_name, quotes)
        else:
            codesDatabase.insert(code_name, quotes, project_id)

    return promptResponse

@prompt_router.get("/projects/{project_id}/codes")
async def list_codes(project_id: int):
    '''
    Lists all the codes for the project in the database, used to list code management
    '''
    print("LIST CODES WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
    database = Codes(config.DB_PATH)
    codes = database.get_codes_by_project(project_id)
    return {
        "codes": [{"id": c[0], "code": c[1], "quotes": c[2]} for c in codes]
    }

@prompt_router.delete("/codes/{code_id}")
async def delete_code(code_id: int):
    #Deletes codes from database
    database = Codes(config.DB_PATH)
    try:
        database.delete(code_id)
        return {"success": True}
    except ValueError:
        raise HTTPException(status_code=404, detail="Code not found")

    
def extract_text(text: str):
    '''
    Regex decoder which takes the text designed by the AI prompt and turns it into a dict object
    '''
    pattern = r"~(.*?)~(.*?)(?=(~|$))" #regex decoder
    matches = re.findall(pattern, text, flags=re.DOTALL)

    codes = {}

    for code_name, content, _ in matches:
        code_name = code_name.strip()

        # Extract quotes for this code
        quotes = re.findall(r"%(.*?)%", content, flags=re.DOTALL)
        quotes = [q.strip() for q in quotes]

        codes[code_name] = quotes

    return codes

    
     

