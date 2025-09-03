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

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---


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
        #Ingest transcription into Vector Database
        #test 
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__),  "projects", config.DEFAULT_PROJECT, "testHolder.txt"))

        try:
            with open(data_path, "w", encoding="utf-8") as f:
                f.write(text_output)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to write transcription file: {e}")
        
        print("process reached")
        print(data_path)
        await process_transcription(data_path)
        
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

async def process_transcription(file_path: str):
    print("process transcription")
    print(file_path)
    qdrant_manager = app.state.qdrant_manager
    qdrant_manager.clear_collection(config.DEFAULT_PROJECT)

    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__),  file_path))
    if os.path.exists(data_path):
        app.state.qdrant_manager.ingest_from_directory(
            config.DEFAULT_PROJECT, data_path)
        print(f"Ingested data for project: {config.DEFAULT_PROJECT}")
    else:
        print(f"Warning: Data path not found, skipping ingestion: {data_path}")

    print("reached end")
    
        
        


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
