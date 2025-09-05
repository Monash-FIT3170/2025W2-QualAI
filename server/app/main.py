from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import traceback
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3
from typing import List, Dict

from app.config import config
import app.api_models as api_models
from app.api_models import PromptRequest
from app.llm_services import generate_online, generate_offline
from app.transcription_service import transcribe_audio_with_diarization
from app.qdrant_manager import QdrantManager


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

    try:
        project_id = app.state.projects_store.insert(
            config.DEFAULT_PROJECT, config.DEFAULT_PROJECT)

        with open(data_path, 'r', encoding='utf-8') as file:
            data_content = file.read()
            app.state.transcripts_store.insert(
                project_id, config.DEFAULT_PROJECT, data_content
            )
    except sqlite3.IntegrityError:
        print(
            f"Default project '{config.DEFAULT_PROJECT}' already exists, skipping creation")
    # ------

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
    template = request.template.lower()

    # Augment the prompt with RAG
    qdrant_manager = app.state.qdrant_manager
    augmented_prompt = qdrant_manager.augment_prompt(prompt, project, template)
    print(f"Augmented Prompt: {augmented_prompt}")

    if mode == "online":
        return await generate_online(augmented_prompt)
    else:
        return await generate_offline(augmented_prompt)

@app.post("/transcribe/")
async def transcribe_endpoint(
    file: UploadFile = File(...,
                            description="Upload an audio file for transcription."),
    project_id: int = Form(...,
                           description="Project ID to save transcription to"),
    project_name: str = Form(...,
                             description="Project name for the transcription")
):
    """
    Transcribe an uploaded audio file using Whisper (CPU, base model).
    Saves the transcription to the specified project.
    """
    # Save the uploaded file
    base_path = Path(__file__).resolve().parent
    uploads_path = base_path / "Interview_Uploads"
    uploads_path.mkdir(exist_ok=True)
    file_path = uploads_path / (file.filename or "default_filename")
   
    try:
        uploads_path = base_path / "Interview Uploads"
        os.makedirs(f"{uploads_path}")
        
        os.chmod(uploads_path, 0o777)
        file_path = uploads_path / file.filename
        os.chmod(file_path, 0o777)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except FileExistsError:
        file_path = uploads_path / file.filename
        os.chmod(file_path, 0o777)
        os.chmod(uploads_path, 0o777)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        print (f"Invalid file format provided")
    
    
    output_filename = f"{file.filename.rsplit('.', 1)[0]}.txt".replace(" ","_")
    output_file_path= uploads_path/output_filename
    #print("run diarize")
    res = await transcribe_audio_with_diarization(file_path)
    #print(res)
    with open(output_file_path, 'r', encoding='utf-8') as ouput_file:
        transcription = ouput_file.read()
        
    # Save the transcription to a .txt file
    # print(output_file_path)
    # print(transcription)
    return {"output_path":output_file_path,"transcription":transcription},

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


@app.get("/projects/{project_id}/transcriptions/{transcription_id}")
def get_transcription(project_id: int, transcription_id: int) -> Dict:
    """
    Get a specific transcription by project and transcription ID.
    """
    # Ensure project exists
    try:
        app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get the transcription
    try:
        proj_id, name, text, processed_at = app.state.transcripts_store.get_transcription_by_id(
            transcription_id)

        # Verify the transcription belongs to the specified project
        if proj_id != project_id:
            raise HTTPException(
                status_code=404, detail="Transcription not found in this project")

        return {
            "transcription_id": transcription_id,
            "project_id": proj_id,
            "name": name,
            "text": text,
            "processed_at": processed_at,
        }
    except LookupError:
        raise HTTPException(status_code=404, detail="Transcription not found")


@app.delete("/projects/{project_id}/transcriptions/{transcription_id}")
def delete_transcription(project_id: int, transcription_id: int):
    """
    Delete a specific transcription by project and transcription ID.
    """
    # Ensure project exists
    try:
        project_name, _, _ = app.state.projects_store.get_project_by_id(
            project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get the transcription first to verify it exists and belongs to the project
    try:
        proj_id, name, text, processed_at = app.state.transcripts_store.get_transcription_by_id(
            transcription_id)

        # Verify the transcription belongs to the specified project
        if proj_id != project_id:
            raise HTTPException(
                status_code=404, detail="Transcription not found in this project")
    except LookupError:
        raise HTTPException(status_code=404, detail="Transcription not found")

    # Delete the transcription from the database
    try:
        app.state.transcripts_store.delete(transcription_id)
        print(
            f"Deleted transcription {transcription_id} from project {project_id}")

        try:
            ### TODO
            ### IMPORTANT - Transcript should be removed from project
            pass
            
        except Exception as vector_error:
            print(
                f"Warning: Failed to update vector database for project '{project_name}': {vector_error}")
            # Don't fail the entire operation if vector update fails

        return {"ok": True, "message": "Transcription deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete transcription: {e}")


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
    Also deletes the corresponding Qdrant collection.
    """
    try:
        # Get project name before deleting (needed for Qdrant collection deletion)
        try:
            project_name, _, _ = app.state.projects_store.get_project_by_id(
                project_id)
        except LookupError:
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete the project from the database (this will also delete associated transcriptions due to foreign key cascade)
        app.state.projects_store.delete(project_id)

        # Delete the corresponding Qdrant collection
        try:
            app.state.qdrant_manager.clear_collection(project_name)
            print(f"Deleted Qdrant collection for project: {project_name}")
        except Exception as qdrant_error:
            print(
                f"Warning: Failed to delete Qdrant collection for project '{project_name}': {qdrant_error}")
            # Don't fail the entire operation if Qdrant deletion fails

        return {"ok": True, "message": "Project deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete project: {e}")
