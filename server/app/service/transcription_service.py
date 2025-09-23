import asyncio
from app.config import config
import os

async def transcribe_audio_with_diarization(recording_path: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    whisper_module_executable_path = os.path.join(current_dir, "whisper-diarization", "diarize.py")

    if not os.path.exists(whisper_module_executable_path):
        return {
            "returncode": -3,
            "stdout": "",
            "stderr": f"diarize.py not found at {whisper_module_executable_path}"
        }

    print("Initializing diarization...")
    print(f"Recording path: {recording_path}")
    
    command = ["python", whisper_module_executable_path, "-a", recording_path]
    print("Running command:", ' '.join(command))

    timeout = config.DIAZARIZATION_TIMEOUT_SECOND

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            try:
                process.kill()
            except Exception as kill_err:
                print(f"[WARN] Failed to kill process: {kill_err}")
            return {
                "returncode": -2,
                "stdout": "",
                "stderr": f"Process timed out after {timeout} seconds"
            }

        result = {
            "returncode": process.returncode,
            "stdout": stdout.decode().strip() if stdout else "",
            "stderr": stderr.decode().strip() if stderr else ""
        }

    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }

    return result
