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
from pydantic import BaseModel

from app.config import config
from app.llm_services import generate_online, generate_offline
from app.transcription_service import Transcriber
from app.qdrant_manager import QdrantManager

DIAZARIZATION_TIMEOUT_SECOND = 30000

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

      

async def diarize_audio(recording_path: str,base_path:str):
        
        whisper_module_executable_path = base_path / "whisper-diarization/diarize.py"
        print("init diarization")
        # Call diarize.py with subprocess
        command = [
            "python", whisper_module_executable_path,
            "-a", recording_path,
        ]
        
        # print(recording_path)
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for process to complete with timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=DIAZARIZATION_TIMEOUT_SECOND)
            except asyncio.TimeoutError:
                try:
                    process.terminate()
                    process.kill()
                except:
                    pass
                raise
            
            result = {
                "returncode": process.returncode,
                "stdout": stdout.decode().strip() if stdout else "",
                "stderr": stderr.decode().strip() if stderr else ""
            }
        # Handle errors
        except asyncio.TimeoutError:
            return {
                "returncode": -2,
                "stdout": "",
                "stderr": f"Process timed out after {DIAZARIZATION_TIMEOUT_SECOND} seconds"
            }
        except Exception as e:
            return e

        return result
        # return {"transcript": transcript}


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(..., description="Upload an audio file for transcription.")):
    """
    Transcribes an uploaded audio file using the Vosk-based Transcriber service.
     :param file: the File path location of the chosen uploaded file functionality on the webpage.
    """
    # Define paths
    base_path = Path(__file__).resolve().parent
    uploads_path = base_path / "Interview_Uploads"
    uploads_path.mkdir(exist_ok=True)
    file_path = uploads_path / (file.filename or "default_filename")
   
    try:
        base_path = Path(__file__).resolve().parent
        print(base_path)
        uploads_path = base_path / "Interview Uploads"
        os.makedirs(f"{uploads_path}")
        
        os.chmod(uploads_path, 0o777)
        file_path = uploads_path / file.filename
        os.chmod(file_path, 0o777)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except FileExistsError:
        base_path = Path(__file__).resolve().parent
        uploads_path = base_path / "Interview Uploads"
        file_path = uploads_path / file.filename
        os.chmod(file_path, 0o777)
        os.chmod(uploads_path, 0o777)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        print (f"Invalid file format provided")
    
    
    output_filename = f"{file.filename.rsplit('.', 1)[0]}.txt".replace(" ","_")
    output_file_path= uploads_path/output_filename
    print("run diarize")
    res = await diarize_audio(file_path)
    print(res)
    with open(filename, 'r', encoding='utf-8') as file:
        transcription = file.read()
        
    # Save the transcription to a .txt file
    
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
