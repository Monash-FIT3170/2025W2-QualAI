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
from app.api.transcription_endpoints import transcription_router
from app.api.transcribe_endpoints import transcribe_router
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

# --- include routers ---
app.include_router(project_router)
app.include_router(transcription_router)
app.include_router(transcribe_router)
app.include_router(prompt_router)


# --- Back-end Status ---
@app.get("/status")
async def get_status():
    return boot_state
