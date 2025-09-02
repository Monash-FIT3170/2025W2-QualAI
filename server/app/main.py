from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path
from pydantic import BaseModel

from app.config import config
from app.llm_services import generate_online, generate_offline
from app.transcription_service import Transcriber
from app.qdrant_manager import QdrantManager
from app import database_models as db
import sqlite3
from typing import List, Dict



# --- Application Setup ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    print("Starting application...")

    # Initialize and ingest data for Qdrant on startup
    app.state.qdrant_manager = QdrantManager()

    # --- this is just for placeholder data to be filled into vector db ---
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__),  "projects", config.DEFAULT_PROJECT, "data.txt"))
    if os.path.exists(data_path):
        app.state.qdrant_manager.ingest_from_directory(
            config.DEFAULT_PROJECT, data_path)
        print(f"Ingested data for project: {config.DEFAULT_PROJECT}")
    else:
        print(f"Warning: Data path not found, skipping ingestion: {data_path}")
    # ------

    # Initialize the transcriber model
    app.state.transcriber = Transcriber(config.VOSK_MODEL_PATH)
    print("Startup complete.")
    yield
    print("Shutting down...")

app = FastAPI(title="QualAI API", lifespan=lifespan)

# --- Middleware ---

# new
DB_PATH = str((Path(__file__).resolve().parent / "qualAI.db"))
projects_store = db.Project(DB_PATH)
transcripts_store = db.Transcription(DB_PATH)



app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---




class ProjectCreate(BaseModel):
    name: str
    description: str = ""

class TranscriptionCreate(BaseModel):
    name: str
    text: str


class PromptRequest(BaseModel):
    prompt: str
    project: str = config.DEFAULT_PROJECT  # default for testing
    mode: str = "offline"  # default = offline

# --- API Endpoints ---


@app.post("/generate")
async def generate_text(request: PromptRequest):
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
async def transcribe_audio(file: UploadFile = File(..., description="Upload an audio file for transcription.")):
    """
    Transcribes an uploaded audio file using the Vosk-based Transcriber service.
    """
    # Define paths
    base_path = Path(__file__).resolve().parent
    uploads_path = base_path / "Interview_Uploads"
    uploads_path.mkdir(exist_ok=True)
    file_path = uploads_path / (file.filename or "default_filename")

    # Save the uploaded file
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save uploaded file: {e}")

    # Transcribe the audio file
    transcriber = app.state.transcriber
    try:
        transcription_raw = await transcriber.transcribe(str(file_path))
        text_output = " ".join(
            segment["text"]
            for segment in transcription_raw["transcription"]
            if segment["text"].strip()
        )

        # Generate a filename for the transcript
        transcript_filename = f"{Path(file.filename).stem}_transcript.txt".replace(
            " ", "_")

        return {"filename": transcript_filename, "transcription": text_output}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Transcription failed: {e}")
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
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


# turning the tuples from the database into json
def _project_row_to_dict(row_id: int, row: tuple) -> Dict:
    # row comes as: (name, description, created_at)
    return {
        "project_id": row_id,
        "name": row[0],
        "description": row[1],
        "created_at": row[2],
    }

def _project_full_row_to_dict(row: tuple) -> Dict:
    # row comes as: (project_id, name, description, created_at)
    return {
        "project_id": row[0],
        "name": row[1],
        "description": row[2],
        "created_at": row[3],
    }

def _transcription_meta_row_to_dict(row: tuple) -> Dict:
    # row comes as: (transcription_id, name, processed_at)
    return {
        "transcription_id": row[0],
        "name": row[1],
        "processed_at": row[2],
    }

def _transcription_full_row_to_dict(project_id: int, row: tuple) -> Dict:
    # row comes as: (project_id, name, transcription, processed_at)
    return {
        "project_id": project_id,
        "name": row[1],
        "text": row[2],
        "processed_at": row[3],
    }


# ------------------------------
# Project & Transcription routes
# ------------------------------

@app.post("/projects")
def create_project(payload: ProjectCreate):
    """
    Create a new project. Name must be unique (sqlite UNIQUE constraint).
    """
    try:
        new_id = projects_store.insert(payload.name, payload.description or "")
    except sqlite3.IntegrityError:
        # UNIQUE(name) violated
        raise HTTPException(status_code=400, detail="Project name already exists.")

    # fetch and return canonical row
    name, desc, created_at = projects_store.get_project_by_id(new_id)
    return _project_row_to_dict(new_id, (name, desc, created_at))


@app.get("/projects")
def list_projects() -> List[Dict]:
    """
    List all projects. If DB is empty, create a default 'Project 1' and return it.
    """
    rows = projects_store.get_all_projects()
    if not rows:
        # auto-create default to keep UX consistent with your current app
        try:
            default_id = projects_store.insert("Project 1", "Default project")
            name, desc, created_at = projects_store.get_project_by_id(default_id)
            return [_project_row_to_dict(default_id, (name, desc, created_at))]
        except sqlite3.IntegrityError:
            # extremely unlikely race; just refetch all
            rows = projects_store.get_all_projects()

    return [_project_full_row_to_dict(r) for r in rows]


@app.get("/projects/{project_id}")
def get_project(project_id: int) -> Dict:
    """
    Get a single project by id.
    """
    try:
        name, desc, created_at = projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    return _project_row_to_dict(project_id, (name, desc, created_at))


@app.post("/projects/{project_id}/transcriptions")
def add_transcription(project_id: int, payload: TranscriptionCreate) -> Dict:
    """
    Attach a transcription to a specific project.
    """
    # Ensure project exists first (will raise LookupError -> 404)
    try:
        projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    new_id = transcripts_store.insert(project_id, payload.name, payload.text)
    # Optionally return minimal info with id, or the full record:
    proj_id, name, text, processed_at = transcripts_store.get_transcription_by_id(new_id)
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
        projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    rows = transcripts_store.get_all_project_transcriptions(project_id)
    return [_transcription_meta_row_to_dict(r) for r in rows]
