from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path
import sqlite3
from typing import List, Dict

from app.config import config
import app.api_models as api_models
from app.llm_services import generate_online, generate_offline
from app.transcription_service import Transcriber
from app.qdrant_manager import QdrantManager
from app.transcribe_logic import load_model, transcribe_audio
from app import database_models as db
from app.helpers.project_converters import (
    project_row_to_dict,
    project_full_row_to_dict,
)
import app.helpers.transcription_converters as trans_conv


# --- Application Setup ---

boot_state = {"status": "booting"}



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    print("Starting application...")
    # Initalise SQL Database
    app.state.projects_store = db.Project(config.DB_PATH)
    app.state.projects_store.insert(config.DEFAULT_PROJECT, config.DEFAULT_PROJECT)
    app.state.transcripts_store = db.Transcription(config.DB_PATH)

    # Initialize and ingest data for Qdrant on startup
    app.state.qdrant_manager = QdrantManager()
    app.state.transcriber = Transcriber(model_size="base")


    # --- this is just for placeholder data to be filled into vector db ---
    data_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__),  "projects", config.DEFAULT_PROJECT, "data.txt"))
    if os.path.exists(data_path):
        app.state.qdrant_manager.ingest_from_directory(
            config.DEFAULT_PROJECT, data_path)
        print(f"Ingested data for project: {config.DEFAULT_PROJECT}")
    else:
        print(f"Warning: Data path not found, skipping ingestion: {data_path}")
    # ------

    # Initialize the transcriber model
    app.state.transcriber = Transcriber(model_size="base")
    print("Startup complete.")
    boot_state["status"] = "online"
    yield
    print("Shutting down...")

app = FastAPI(title="QualAI API", lifespan=lifespan)

# --- Middleware ---




app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# --- Back-end Status ---

@app.get("/status")
async def get_status():
    return boot_state


# --- API Models ---

class PromptRequest(BaseModel):
    prompt: str
    project: str = config.DEFAULT_PROJECT  # default for testing
    mode: str = "offline"  # default = offline



# --- API Endpoints ---

@app.post("/generate")
async def generate_text(request: api_models.PromptRequest):
    """
    Generates a text response using either an online (Gemini) or offline (Ollama) model.
    The prompt is augmented with context from a Qdrant vector database.
    """
    prompt = request.prompt.strip()
    mode = request.mode.lower()
    project = request.project

    # Augment the prompt with RAG
    qdrant_manager = app.state.qdrant_manager
    augmented_prompt = qdrant_manager.augment_prompt(prompt, project)
    print(f"Augmented Prompt: {augmented_prompt}")

    if mode == "online":
        return await generate_online(augmented_prompt)
    else:
        return await generate_offline(augmented_prompt)


@app.post("/transcribe/")
async def transcribe_endpoint(file: UploadFile = File(..., description="Upload an audio file for transcription.")):
    """
    Transcribe an uploaded audio file using Whisper (CPU, base model).
    """
    # Save the uploaded file
    base_path = Path(__file__).resolve().parent
    uploads_path = base_path / "Interview_Uploads"
    uploads_path.mkdir(exist_ok=True)
    file_path = uploads_path / (file.filename or "default_filename")

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save uploaded file: {e}"
        )

    try:
        transcriber = app.state.transcriber
        result = await transcriber.transcribe(str(file_path), language="en")
        text_output = result.get("text", "")

        transcript_filename = (
            f"{Path(file.filename).stem}_transcript.txt".replace(" ", "_")
        )

        return {"filename": transcript_filename, "transcription": text_output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

    finally:
        if file_path.exists():
            os.remove(file_path)


@app.post("/download/")
async def download_transcription(final_output: str = Form(...), filename: str = Form(...)):
    """
    Saves the final transcription text to a file and provides it for download.
    """
    base_path = Path(__file__).resolve().parent
    download_path = base_path / "Transcripts"
    download_path.mkdir(exist_ok=True)

    file_path = download_path / filename

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_output)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to write transcription file: {e}")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='text/plain'
    )



@app.post("/projects/{project_id}/transcriptions")
def add_transcription(project_id: int, payload: api_models.Transcription) -> Dict:
    """
    Attach a transcription to a specific project.
    """
    # Ensure project exists first (will raise LookupError -> 404)
    try:
        app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    new_id = app.state.transcripts_store.insert(
        project_id, payload.name, payload.text)
    # Optionally return minimal info with id, or the full record:
    proj_id, name, text, processed_at = app.state.transcripts_store.get_transcription_by_id(
        new_id)
    return {
        "transcription_id": new_id,
        "project_id": proj_id,
        "name": name,
        "text": text,
        "processed_at": processed_at,
    }


@app.get("/projects/{project_id}/transcriptions")
def list_transcriptions(project_id: int) -> List[Dict]:
    """
    List transcription metadata for a project (no full text).
    """
    # Ensure project exists
    try:
        app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    rows = app.state.transcripts_store.get_all_project_transcriptions(
        project_id)
    return [trans_conv.transcription_meta_row_to_dict(r) for r in rows]


@app.post("/projects")
def create_project(payload: api_models.Project):
    """
    Create a new project. Name must be unique (sqlite UNIQUE constraint).
    """
    try:
        new_id = app.state.projects_store.insert(
            payload.name, payload.description or "")
    except sqlite3.IntegrityError:
        # UNIQUE(name) violated
        raise HTTPException(
            status_code=400, detail="Project name already exists.")

    # fetch and return canonical row
    name, desc, created_at = app.state.projects_store.get_project_by_id(new_id)
    return project_row_to_dict(new_id, (name, desc, created_at))


@app.get("/projects")
def list_projects() -> List[Dict]:
    """
    List all projects. If DB is empty, create a default 'Project 1' and return it.
    """
    rows = app.state.projects_store.get_all_projects()
    if not rows:
        # auto-create default to keep UX consistent with your current app
        try:
            default_id = app.state.projects_store.insert(
                "Project 1", "Default project")
            name, desc, created_at = app.state.projects_store.get_project_by_id(
                default_id)
            return project_row_to_dict(default_id, (name, desc, created_at))
        except sqlite3.IntegrityError:
            # extremely unlikely race; just refetch all
            rows = app.state.projects_store.get_all_projects()

    return [project_full_row_to_dict(r) for r in rows]


@app.get("/projects/{project_id}")
def get_project(project_id: int) -> Dict:
    """
    Get a single project by id.
    """
    try:
        name, desc, created_at = app.state.projects_store.get_project_by_id(
            project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    return project_row_to_dict(project_id, (name, desc, created_at))

@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    """
    Delete a project by id.
    """
    try:
        app.state.projects_store.delete(project_id)  
        return {"ok": True, "message": "Project deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {e}")
