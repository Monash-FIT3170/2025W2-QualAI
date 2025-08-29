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
from vosk import Model, KaldiRecognizer
from pathlib import Path
from app import database_models as db


SAMPLE_RATE = 16000
CHUNK_SIZE = 4000

app = FastAPI()

# new
DB_PATH = str((Path(__file__).resolve().parent / "qualAI.db"))
projects_store = db.Project(DB_PATH)
transcripts_store = db.Transcription(DB_PATH)



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



class ProjectCreate(BaseModel):
    name: str
    description: str = ""

class TranscriptionCreate(BaseModel):
    name: str
    text: str


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
    



class Transcriber:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise ValueError(f"Model path not found: {model_path}")
        self.model_path = model_path
        self.model = Model(model_path)

    async def fmt(self, data):
        data = json.loads(data)
        result = data.get("result", [{"start": 0, "end": 0}])
        start = min(r["start"] for r in result) if result else 0
        end = max(r["end"] for r in result) if result else 0

        return {
            "start": str(timedelta(seconds=start)),
            "end": str(timedelta(seconds=end)),
            "text": data.get("text", ""),
        }

    async def transcribe(self, recording_path: str):
        rec = KaldiRecognizer(self.model, SAMPLE_RATE)
        rec.SetWords(True)

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"File not found: {self.model_path}")

        transcription = []
        ffmpeg_command = [
            "ffmpeg",
            "-nostdin",
            "-loglevel",
            "quiet",
            "-i",
            recording_path,
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "1",
            "-f",
            "s16le",
            "-",
        ]

        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,  # Capture stderr for potential errors
        )

        while True:
            if process.stdout is None:
                break
            data = await process.stdout.read(CHUNK_SIZE)
            print("read chunk")
            if not data:
                break
            if rec.AcceptWaveform(data):
                transcription.append(await self.fmt(rec.Result()))

        transcription.append(await self.fmt(rec.FinalResult()))

        return {"transcription": transcription}


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

        file_path = uploads_path / file.filename
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except FileExistsError:
        base_path = Path(__file__).resolve().parent
        uploads_path = base_path / "Interview Uploads"
        file_path = uploads_path / file.filename

        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        print (f"Invalid file format provided")
    

    model_path = "/app/app/vosk-model-en-us-0.22-lgraph"  # Ensure this path is correct
    transcriber = Transcriber(model_path)

    transcription_raw = await transcriber.transcribe(file_path)
    text_output = " ".join(
        segment["text"]
        for segment in transcription_raw["transcription"]
        if segment["text"].strip()
    )
    # Save the transcription to a .txt file
    transcript_filename = f"{file.filename.rsplit('.', 1)[0]}_transcript.txt".replace(" ","_")

    # # Return a download link
    # html_content = f"""
    # <!DOCTYPE html>
    # <html>
    #     <head><title>Transcription Complete</title></head>
    #     <body>
    #         <h2>Transcription Complete</h2>
            
    #         <form method="post" action="/download/">
    #             <input name = "filename" type = "hidden" value = {transcript_filename}></input>
    #             <textarea name = "final_output" cols="50" rows="10">{text_output}</textarea> <br>
    #             <button type="Download">Download Transcript</button>
    #         </form>
    #         <form action = "/transcribe/">
    #             <button type="Return">Back</button>
    #         </form>
    #     </body>
    # </html>
    # """
    # return HTMLResponse(content=html_content, status_code=200)

    return {"filename":transcript_filename,"transcription":text_output}


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
    
    
@app.post("/projects")
def create_project(name: str, description: str = "", db: Session = Depends(get_db)):
    project = Project(name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@app.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {"error": "Project not found"}
    return project



# these are routes that connect to the SQLite models that we have for projects and transcriptions.
#API endpoints


@app.post("/projects")
def create_project(body: ProjectCreate):
    pid = projects_store.insert(body.name, body.description)
    return {"project_id": pid, "name": body.name, "description": body.description}

@app.get("/projects")
def list_projects():
    rows = projects_store.get_all_projects()
    # rows: List[Tuple[int, str, str, str]] -> (project_id, name, description, created_at)
    return [
        {"project_id": pid, "name": name, "description": desc, "created_at": created_at}
        for (pid, name, desc, created_at) in rows
    ]

@app.get("/projects/{project_id}")
def get_project(project_id: int):
    try:
        name, desc, created_at = projects_store.get_project_by_id(project_id)
        return {"project_id": project_id, "name": name, "description": desc, "created_at": created_at}
    except LookupError:
        return {"error": "Project not found"}

@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    try:
        projects_store.delete(project_id)
        return {"ok": True}
    except ValueError:
        return {"error": "Project not found"}


@app.post("/projects/{project_id}/transcriptions")
def add_transcription(project_id: int, body: TranscriptionCreate):
    tid = transcripts_store.insert(project_id, body.name, body.text)
    return {"transcription_id": tid, "project_id": project_id, "name": body.name}

@app.get("/projects/{project_id}/transcriptions")
def list_transcriptions(project_id: int):
    rows = transcripts_store.get_all_project_transcriptions(project_id)
    # rows: List[Tuple[int, str, str]] -> (transcription_id, name, processed_at)
    return [{"transcription_id": tid, "name": name, "processed_at": ts} for (tid, name, ts) in rows]

@app.get("/transcriptions/{transcription_id}")
def get_transcription(transcription_id: int):
    try:
        project_id, name, text, processed_at = transcripts_store.get_transcription_by_id(transcription_id)
        return {"transcription_id": transcription_id, "project_id": project_id, "name": name, "text": text, "processed_at": processed_at}
    except LookupError:
        return {"error": "Transcription not found"}
    
# this is to add a second endpoint that transcribes and stores into DB after vosk
@app.post("/transcribe/{project_id}")
async def transcribe_audio_for_project(
    project_id: int,
    file: UploadFile = File(..., description="Upload an interview for transcription here")
):
    # ... your existing transcribe code up to text_output ...
    transcript_filename = f"{file.filename.rsplit('.', 1)[0]}_transcript.txt".replace(" ","_")
    tid = transcripts_store.insert(project_id, transcript_filename, text_output)
    return {"filename": transcript_filename, "transcription": text_output, "project_id": project_id, "transcription_id": tid}
