import os
import json
import asyncio
from datetime import timedelta
from vosk import Model, KaldiRecognizer
from fastapi import HTTPException

from .config import config

class Transcriber:
    """
    A service class for handling audio transcription using Vosk.
    """
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise ValueError(f"Model path not found: {model_path}")
        self.model = Model(model_path)

    async def _format_result(self, data_str: str) -> dict:
        """
        Formats a single transcription result segment.
        """
        data = json.loads(data_str)
        result = data.get("result", [])
        start = min((r.get("start", 0) for r in result), default=0)
        end = max((r.get("end", 0) for r in result), default=0)

        return {
            "start": str(timedelta(seconds=start)),
            "end": str(timedelta(seconds=end)),
            "text": data.get("text", ""),
        }

    async def transcribe(self, recording_path: str) -> dict:
        """
        Transcribes an audio file using ffmpeg and Vosk.

        Args:
            recording_path: The path to the audio file to be transcribed.

        Returns:
            A dictionary containing the full transcription.
        """
        if not os.path.exists(recording_path):
            raise FileNotFoundError(f"Audio file not found: {recording_path}")

        recognizer = KaldiRecognizer(self.model, config.SAMPLE_RATE)
        recognizer.SetWords(True)

        ffmpeg_command = [
            "ffmpeg", "-nostdin", "-loglevel", "quiet",
            "-i", recording_path,
            "-ar", str(config.SAMPLE_RATE),
            "-ac", "1", "-f", "s16le", "-",
        ]

        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        transcription = []
        while True:
            if process.stdout is None:
                break
            data = await process.stdout.read(config.CHUNK_SIZE)
            if not data:
                break
            if recognizer.AcceptWaveform(data):
                transcription.append(await self._format_result(recognizer.Result()))

        transcription.append(await self._format_result(recognizer.FinalResult()))
        
        # Check for errors from ffmpeg
        stderr_data = await process.communicate()
        if process.returncode != 0:
            error_message = stderr_data[1].decode().strip()
            raise HTTPException(status_code=500, detail=f"ffmpeg error: {error_message}")

        return {"transcription": transcription}