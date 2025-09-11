import os
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.config import config

transcribe_router = APIRouter()


@transcribe_router.post("/transcribe/")
async def transcribe_endpoint(
    request: Request,
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
        transcriber = request.app.state.transcriber
        result = await transcriber.transcribe(str(file_path), language="en")
        text_output = result.get("text", "")

        transcript_filename = f"{Path(file.filename).stem}_transcript.txt".replace(
            " ", "_"
        )

        # Save transcription to the database
        transcription_id = request.app.state.transcripts_store.insert(
            project_id, transcript_filename, text_output
        )

        # Ingest transcription into Vector Database
        request.app.state.qdrant_manager.clear_collection(config.DEFAULT_PROJECT)
        # for now uses default project, this should change based on project management tools
        request.app.state.qdrant_manager.ingest_from_text(project_name, text_output)

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


@transcribe_router.post("/download/")
async def download_transcription(
    request: Request, final_output: str = Form(...), filename: str = Form(...)
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
