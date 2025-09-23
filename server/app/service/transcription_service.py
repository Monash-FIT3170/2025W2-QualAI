import asyncio
from config import config
async def transcribe_audio_with_diarization(recording_path: str):
    """
    Function to generate transcription from the audio file with whisper-diarization
    param: 
        recording_path : the path of the uploaded 
    output:
        result The 

    """
    whisper_module_executable_path = "whisper-diarization/diarize.py"
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
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout= config.DIAZARIZATION_TIMEOUT_SECOND)
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
            "stderr": f"Process timed out after { config.DIAZARIZATION_TIMEOUT_SECOND} seconds"
        }
    except Exception as e:
        return e

    return result
    # return {"transcript": transcript}
