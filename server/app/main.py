from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path
import sqlite3

from app.config import config
from app.api.models import PromptRequest
from app.llm_services import generate_online, generate_offline
from app.transcription_service import Transcriber
from app.qdrant_manager import QdrantManager
from app.database import Project, Transcription
from app.api.project_api import router as project_router
from app.api.transcription_api import router as transcription_router


# --- Application Setup ---

boot_state = {"status": "booting"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    print("Starting application...")
    # Initalise SQL Database
    app.state.projects_store = Project(config.DB_PATH)
    app.state.transcripts_store = Transcription(config.DB_PATH)

    # Initialize and ingest data for Qdrant on startup
    app.state.qdrant_manager = QdrantManager()
    app.state.transcriber = Transcriber(model_size="base")

    # --- this is just for placeholder data to be filled into vector db ---
    data_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "projects", config.DEFAULT_PROJECT, "data.txt"
        )
    )
    if os.path.exists(data_path):
        app.state.qdrant_manager.ingest_from_directory(
            config.DEFAULT_PROJECT, data_path
        )
        print(f"Ingested data for project: {config.DEFAULT_PROJECT}")
    else:
        print(f"Warning: Data path not found, skipping ingestion: {data_path}")

    try:
        project_id = app.state.projects_store.insert(
            config.DEFAULT_PROJECT, config.DEFAULT_PROJECT
        )

        with open(data_path, "r", encoding="utf-8") as file:
            data_content = file.read()
            app.state.transcripts_store.insert(
                project_id, config.DEFAULT_PROJECT, data_content
            )
    except sqlite3.IntegrityError:
        print(
            f"Default project '{config.DEFAULT_PROJECT}' already exists, skipping creation"
        )
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


app.include_router(project_router)
app.include_router(transcription_router)


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
    file: UploadFile = File(..., description="Upload an audio file for transcription."),
    project_id: int = Form(..., description="Project ID to save transcription to"),
    project_name: str = Form(..., description="Project name for the transcription"),
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
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save uploaded file: {e}"
        )

    # Transcribe the file using Whisper
    text_output = ""

    try:
        transcriber = app.state.transcriber
        result = await transcriber.transcribe(str(file_path), language="en")
        text_output = result.get("text", "")

        transcript_filename = f"{Path(file.filename).stem}_transcript.txt".replace(
            " ", "_"
        )

        # Save transcription to the database
        transcription_id = app.state.transcripts_store.insert(
            project_id, transcript_filename, text_output
        )

        # Ingest transcription into Vector Database
        app.state.qdrant_manager.clear_collection(config.DEFAULT_PROJECT)
        # for now uses default project, this should change based on project management tools
        app.state.qdrant_manager.ingest_from_text(project_name, text_output)

        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "filename": transcript_filename,
            "transcription": text_output,
            "transcription_id": transcription_id,
            "project_id": project_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")


@app.post("/download/")
async def download_transcription(
    final_output: str = Form(...), filename: str = Form(...)
):
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
            status_code=500, detail=f"Failed to write transcription file: {e}"
        )

    return FileResponse(path=file_path, filename=filename, media_type="text/plain")
