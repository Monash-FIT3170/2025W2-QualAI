import os
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from app.service.transcription_service import transcribe_audio_with_diarization
from app.config import config

transcribe_router = APIRouter()


@transcribe_router.post("/transcribe/")
async def transcribe_endpoint(
    request: Request,
    file: UploadFile = File(..., description="Upload an audio file for transcription."),
    project_id: int = Form(..., description="Project ID to save transcription to"),
):
    """
    Transcribe an uploaded audio file using Whisper (CPU, base model).
    Saves the transcription to the specified project.
    """
    # Save the uploaded file
    uploads_path = config.BASE_PATH / "Interview_Uploads"
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
        result = await transcribe_audio_with_diarization(str(file_path))
        # Define the original transcript path (produced by the function)
        original_transcript_path = uploads_path / f"{Path(file.filename).stem}.txt"

        # Define the renamed transcript filename and path
        transcript_filename = f"{Path(file.filename).stem}_transcript.txt".replace(" ", "_")
        output_file_path = uploads_path / transcript_filename

        # Rename the file
        if original_transcript_path.exists():
            os.rename(original_transcript_path, output_file_path)
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Expected output file not found: {original_transcript_path}"
            )

        print("Renamed transcript file to:", output_file_path)
       
        print("reading output")
        with open(output_file_path, 'r', encoding='utf-8') as ouput_file:
            text_output = ouput_file.read()
            print("read output")
        # Save transcription to the database
        transcription_id = request.app.state.transcripts_store.insert(
            project_id, transcript_filename, text_output
        )
        print("1")
        # Ingest transcription into Vector Database
        request.app.state.qdrant_manager.clear_collection(project_id)
        # for now uses default project, this should change based on project management tools
        request.app.state.qdrant_manager.ingest_from_text(project_id, text_output)
        print("2")
        if os.path.exists(file_path):
            os.remove(file_path)
        print("3")
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
    download_path = config.BASE_PATH / "Transcripts"
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
