import os
import json
import asyncio
from datetime import timedelta
from fastapi import HTTPException
import whisper
from .config import config

class Transcriber:
    """
    A service class for handling audio transcription using Vosk.
    """
    def __init__(self, model_size: str = "base"):
        print(f"Loading Whisper model: {model_size} ...")
        self.model = whisper.load_model(model_size)

    async def _format_result(self, segment: dict) -> dict:
        """
        Formats a single transcription result segment.
        """
        start = segment.get("start", 0)
        end = segment.get("end", 0)
        return {
            "start": str(timedelta(seconds=start)),
            "end": str(timedelta(seconds=end)),
            "text": segment.get("text", "").strip(),
        }
    


    async def transcribe(self, recording_path: str, language: str = None) -> dict:
        """
        Transcribes an audio file using ffmpeg and Vosk.

        Args:
            recording_path: The path to the audio file to be transcribed.

        Returns:
            A dictionary containing the full transcription.
        """
        if not os.path.exists(recording_path):
            raise FileNotFoundError(f"Audio file not found: {recording_path}")

        try:
            # Whisper does the ffmpeg conversion internally
            result = await asyncio.to_thread(
                self.model.transcribe, recording_path, language=language
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Whisper error: {str(e)}")

        transcription = [
            await self._format_result(segment) for segment in result.get("segments", [])
        ]

        return {"text": result.get("text", ""), "segments": transcription}