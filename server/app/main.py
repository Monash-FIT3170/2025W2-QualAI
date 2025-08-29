from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import traceback
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
import asyncio
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

SAMPLE_RATE = 16000
CHUNK_SIZE = 4000
DIAZARIZATION_TIMEOUT_SECOND = 30000

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with actual frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Sets the Default root html page for the transcription application, details transcription application capabilities
    """

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Audio Transcription API</title>
    </head>
    <body>
        <h1>Welcome to the Audio Transcription API</h1>
        <p>Use the <code>/transcribe/</code> endpoint to upload an audio file for transcription.</p>
        <p>Supported formats: mp3, wav, ogg, flac.</p>
        <form action="/transcribe/">
            <button type="submit">Go to the /Transcribe/ endpoint</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)  

class PromptRequest(BaseModel):
    prompt: str

OLLAMA_URL = "http://ollama:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:7b"

@app.post("/generate")
async def generate_text(request: PromptRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": request.prompt,
                    "stream": False
                },
                    timeout=60.0
            )
        if response.status_code != 200:
            print("OLLAMA Error:", response.text)
            return {"error": response.text}
        
        # Log what Ollama actually returned
        json_response = response.json()
        # print("OLLAMA Response:", json_response)
        
        # Return only the part you care about
        return {"response": json_response.get("response", "No 'response' field in Ollama reply")}
    
    except Exception as e:
        error_details = traceback.format_exc()
        # print("Server Error Traceback:\n", error_details)
        return {"error": str(e) or "Unknown server error"}
    

async def diarize_audio(recording_path: str):
        base_path = Path(__file__).resolve().parent
        whisper_module_path=base_path / "whisper-diarization/diarize.py"
        print("init diarization")
        # Call diarize.py with subprocess
        command = [
            "python", whisper_module_path,
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



@app.get("/transcribe/")
async def transcribe_form():
    """
    Form page opened when the Transcribe Button has been implemented, holds the UI data for uploading and initialising transcription.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Audio Transcriber</title>
        </head>
        <body>
            <h2>Upload an interview for transcription</h2>
            <form action="/transcribe/" enctype="multipart/form-data" method="post">
                    <input type="file" name="file">
                    <input type ="submit" value = "Transcribe">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(html_content, status_code=200)


@app.post("/transcribe/")
async def transcribe_audio(
    file: UploadFile = File(
        ..., description="Upload an interview for transcription here"
    )
):
    """
    Function for transcribing audio using the Transcriber object, creates an upload directory for files and returns a editable transcription page.

    :param file: the File path location of the chosen uploaded file functionality on the webpage.
    """
    
    try:
        base_path = Path(__file__).resolve().parent
        uploads_path = base_path / "Interview Uploads"
        os.makedirs(f"{uploads_path}")
        os.chmod(uploads_path, 0o777)
        file_path = uploads_path / file.filename
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except FileExistsError:
        base_path = Path(__file__).resolve().parent
        uploads_path = base_path / "Interview Uploads"
        file_path = uploads_path / file.filename
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

    # Save the transcription to a .txt file
    
    return {"output_path":output_file_path}

@app.post("/download/")
async def download_transcription(final_output: str = Form(...), filename: str=Form(...)):
    """
    Function for downloading the edited transcription into a local text file.

    :param final_output: The final text file output derived from the text contained in the editable text box from the transcription page
    :param filename: The modified name of the file, used to generate a downloadable text file of the same name. Stored in the transcription page prior.
    """
    base_path = Path(__file__).resolve().parent
    upload_path = base_path / "Interview Uploads"
    os.makedirs(upload_path, exist_ok=True) #should suppress error if directory exists

    file_path = upload_path / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_output)
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='text/plain'
    )
    
    
