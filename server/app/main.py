from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path
from pydantic import BaseModel
from vosk import Model, KaldiRecognizer

from app.config import config
from app.llm_services import generate_online, generate_offline
from app.transcription_service import Transcriber
from app.qdrant_manager import QdrantManager
import sys

SAMPLE_RATE = 16000
CHUNK_SIZE = 4000


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    print("Starting application...")

    # Initialize and ingest data for Qdrant on startup
    app.state.qdrant_manager = QdrantManager()

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
        app.state.qdrant_manager.ingest_from_text(config.DEFAULT_PROJECT, text_output) #for now uses default project, this should change based on project management tools
        

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




"""START OF FEATURES"""
# allows for retrieving all documents from the vector database for display
@app.get("/documents")
async def get_all_documents(project_name: str):
    """
    Retrieves all documents from the vector database for display.
    """
    try:
        # Get all documents from the collection
        client = app.state.qdrant_manager._get_qdrant_client()
        
        # Get all points from the collection
        all_points = client.scroll(
            collection_name=project_name,
            limit=1000,  # Adjust this limit as needed
            with_payload=True,
            with_vectors=False
        )
        
        # Extract document content
        documents = []
        for point in all_points[0]:  # all_points[0] contains the points
            if point.payload and 'page_content' in point.payload:
                documents.append({
                    'id': point.id,
                    'content': point.payload['page_content'],
                    'metadata': point.payload.get('metadata', {})
                })
        
        # Concatenate all document contents
        full_text = " ".join([doc['content'] for doc in documents])
        
        return {
            "documents": documents,
            "full_text": full_text,
            "total_documents": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# breaks down the vector database into collections of per-file documents
@app.get("/collections")
async def list_collections():
    try:
        client = app.state.qdrant_manager._get_qdrant_client()
        cols = client.get_collections().collections
        return {"collections": [c.name for c in cols if c.name.startswith("paper_")]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{collection}")
async def get_documents_by_collection(collection: str):
    try:
        client = app.state.qdrant_manager._get_qdrant_client()
        points, _ = client.scroll(
            collection_name=collection,
            limit=1000,
            with_payload=True,
            with_vectors=False,
        )
        documents = []
        for p in points:
            content = p.payload.get('page_content') if p.payload else None
            metadata = p.payload.get('metadata') if p.payload else {}
            if content:
                documents.append({"id": p.id, "content": content, "metadata": metadata})
        full_text = " ".join([d["content"] for d in documents])
        return {"collection": collection, "documents": documents, "full_text": full_text, "total_documents": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""END OF FEATURES"""




#Probs delete this
"""@app.post("/ingest")
async def ingest_per_file():
    try:
        script_path = Path("/app/scripts/ingest.py")
        result = run_subprocess([sys.executable, str(script_path)], capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)
        # return updated collection list
        client = get_qdrant_client()
        cols = client.get_collections().collections
        return {"ok": True, "stdout": result.stdout, "collections": [c.name for c in cols if not c.name.startswith('.internal')]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""
