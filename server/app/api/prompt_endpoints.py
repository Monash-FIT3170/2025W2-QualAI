from fastapi import APIRouter, Request, HTTPException
from app.api.models import PromptRequest
from app.service.llm_services import generate_offline, generate_online

from app.database.Codes import Codes
from app.database.Themes import Theme
from app.qdrant.qdrant_templates import QDrantTemplates
from app.config import config
import re
import json

prompt_router = APIRouter()


@prompt_router.post("/generate/")
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
    augmented_prompt = qdrant_manager.augment_prompt(prompt, project_id, template)
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
        # return promptResponse
    else:
        promptResponse = await generate_offline(augmented_prompt)
        # return promptResponse

    promptResponseText = promptResponse["response"]
    codes = extract_text(promptResponseText)
    print(codes)

    codesDatabase = Codes(config.DB_PATH)
    codesDatabase.clear_codes_by_project(
        project_id
    )  # clear codes instead of appending them

    existing_codes = {name for _, name, _, _ in codesDatabase.get_all_codes()}

    # insert or update code based on database storage
    for code_name, quotes in codes.items():
        if code_name in existing_codes:
            # update existing code instead
            code_id = next(
                c[0] for c in codesDatabase.get_all_codes() if c[1] == code_name
            )
            codesDatabase.update(code_id, code_name, quotes)
        else:
            codesDatabase.insert(code_name, quotes, project_id)

    return promptResponse


@prompt_router.get("/projects/{project_id}/codes")
async def list_codes(project_id: int):
    """
    Lists all the codes for the project in the database, used to list code management
    """
    print("LIST CODES WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
    database = Codes(config.DB_PATH)
    codes = database.get_codes_by_project(project_id)
    return {"codes": [{"id": c[0], "code": c[1], "quotes": c[2]} for c in codes]}


@prompt_router.delete("/codes/{code_id}")
async def delete_code(code_id: int):
    # Deletes codes from database
    database = Codes(config.DB_PATH)
    try:
        database.delete(code_id)
        return {"success": True}
    except ValueError:
        raise HTTPException(status_code=404, detail="Code not found")


def extract_text(text: str):
    """
    Regex decoder which takes the text designed by the AI prompt and turns it into a dict object
    """
    pattern = r"~(.*?)~(.*?)(?=(~|$))"  # regex decoder
    matches = re.findall(pattern, text, flags=re.DOTALL)

    codes = {}

    for code_name, content, _ in matches:
        code_name = code_name.strip()

        # Extract quotes for this code
        quotes = re.findall(r"%(.*?)%", content, flags=re.DOTALL)
        quotes = [q.strip() for q in quotes]

        codes[code_name] = quotes

    return codes


@prompt_router.post("/generate_themes")
async def generate_themes(request: Request, payload: dict):
    try:
        project_id = payload["project_id"]

        # Get codes
        codes_db = Codes(config.DB_PATH)
        codes = codes_db.get_codes_by_project(project_id)

        if not codes:
            return {"themes": []}

        # Format codes
        codes_data = {
            "codes": [
                {
                    "name": code[1],
                    "quotes": (
                        json.loads(code[2]) if isinstance(code[2], str) else code[2]
                    ),
                }
                for code in codes
            ]
        }

        # Generate themes
        prompt = QDrantTemplates.generate_themes_template(codes_data)
        result = await generate_online(prompt)

        if not result or "response" not in result:
            raise ValueError("No AI response received")

        # Extract and clean response
        response_text = result["response"].strip()

        # Find JSON object in response
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON object found in response")

        json_text = response_text[json_start:json_end]

        try:
            themes_data = json.loads(json_text)
        except json.JSONDecodeError:
            print(f"Invalid JSON: {json_text}")
            raise ValueError("Invalid JSON structure in response")

        if "themes" not in themes_data:
            raise ValueError("Response missing 'themes' key")

        # Store themes
        theme_db = Theme(config.DB_PATH)
        theme_db.clear_themes_by_project(project_id)

        stored_themes = []
        for theme in themes_data["themes"]:
            if (
                not isinstance(theme, dict)
                or "name" not in theme
                or "codes" not in theme
            ):
                continue

            theme_id = theme_db.insert(
                project_id=project_id, theme_name=theme["name"], codes=theme["codes"]
            )
            stored_themes.append(
                {"id": theme_id, "name": theme["name"], "codes": theme["codes"]}
            )

        if not stored_themes:
            raise ValueError("No valid themes generated")

        return {"themes": stored_themes}

    except Exception as e:
        print(f"Theme generation error: {str(e)}")
        print(f"Response text: {result.get('response', 'No response')}")
        raise HTTPException(status_code=500, detail=str(e))


@prompt_router.get("/projects/{project_id}/themes")
async def list_themes(project_id: int):
    """Lists all themes for a project"""
    theme_db = Theme(config.DB_PATH)
    themes = theme_db.get_themes_by_project(project_id)
    return {
        "themes": [
            {"id": t[0], "name": t[1], "codes": json.loads(t[2])} for t in themes
        ]
    }


@prompt_router.delete("/themes/{theme_id}")
async def delete_theme(theme_id: int):
    """Deletes a theme from the database"""
    theme_db = Theme(config.DB_PATH)
    try:
        theme_db.delete(theme_id)
        return {"success": True}
    except ValueError:
        raise HTTPException(status_code=404, detail="Theme not found")
