from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sqlite3

from app.config import config
from app.service.transcription_service import Transcriber
from app.qdrant.qdrant_manager import QdrantManager
from app.database import Project, Transcription
from app.api.project_endpoints import project_router
from app.api.project_transcription_endpoints import transcription_router
from app.api.media_transcriber_endpoints import transcribe_router
from app.api.prompt_endpoints import prompt_router


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
    project_id = None
    try:
        project_id = app.state.projects_store.insert(
            project_name=config.DEFAULT_PROJECT
        )
    except sqlite3.IntegrityError:
        print(
            f"Default project '{config.DEFAULT_PROJECT}' already exists, skipping creation"
        )
        

    data_path = config.DEFAULT_TRANSCRIPTION_PATH
    if os.path.exists(data_path) and project_id is not None:
        app.state.qdrant_manager.ingest_from_directory(
            project_id=project_id, transcription_path=data_path
        )
        print(f"Ingested data for project: {config.DEFAULT_PROJECT}")

        try:
            with open(data_path, "r", encoding="utf-8") as file:
                data_content = file.read()
                app.state.transcripts_store.insert(
                    project_id=project_id,
                    name=config.DEFAULT_TRANSCRIPTION_NAME,
                    transcription=data_content,
                )
        except sqlite3.IntegrityError:
            print(
                f"Default project '{config.DEFAULT_PROJECT}' already exists, skipping creation"
            )
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

# --- include routers ---
app.include_router(project_router)
app.include_router(transcription_router)
app.include_router(transcribe_router)
app.include_router(prompt_router)


# --- Back-end Status ---
@app.get("/status")
async def get_status():
    return boot_state
