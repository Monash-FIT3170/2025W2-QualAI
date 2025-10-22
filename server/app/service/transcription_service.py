import asyncio
import os
from app.config import config

# Assuming you refactored diarize.py to contain a function named transcribe_and_diarize
from app.service.whisper_diarization.diarize import transcribe_and_diarize


async def transcribe_audio_with_diarization(recording_path: str,diarization: bool):
    if not os.path.exists(recording_path):
        return {
            "returncode": -3,
            "stdout": "",
            "stderr": f"Audio file not found at {recording_path}"
        }

    print("Initializing ...")
    print(f"Recording path: {recording_path}")

    timeout = config.DIAZARIZATION_TIMEOUT_SECOND

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(transcribe_and_diarize,recording_path,diarization),
            timeout=timeout
        )

        return {
            "returncode": 0,
            "stdout": f"Transcript saved at {result['transcript_file']}",
            "stderr": ""
        }

    except asyncio.TimeoutError:
        return {
            "returncode": -2,
            "stdout": "",
            "stderr": f"Process timed out after {timeout} seconds"
        }

    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }