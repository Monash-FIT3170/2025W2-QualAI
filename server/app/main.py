from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
from dotenv import load_dotenv
import traceback
import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

import httpx
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vosk import Model, KaldiRecognizer
from .vector import get_db

import requests

SAMPLE_RATE = 16000
CHUNK_SIZE = 4000


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Loading models and connecting to DB...")
    get_db()
    print("Application startup complete.")
    yield
    print("Application shutdown: Cleaning up resources...")




app = FastAPI(title="QualAI API", lifespan=lifespan)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with actual frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    mode: str = "offline" # default = offline

OLLAMA_URL = "http://ollama:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:7b"
env_path = Path(__file__).resolve().parent.parent / '.env'
print(f"Loading .env from: {env_path}")
load_dotenv(dotenv_path=env_path)  # loads variables from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))

@app.post("/generate")
async def generate_text(request: PromptRequest):
    prompt = request.prompt.strip()
    mode = request.mode.lower()
    if mode == "online": 
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            print("Gemini API response:", data)

            # Extract text from Gemini's response
            reply = data["candidates"][0]["content"]["parts"][0]["text"]

            return {"response": reply.strip()}

        except Exception as e:
            return {"response": f"Online mode failed: {str(e)}"}


    else: 
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
    
#Vector DB Things
class SearchResponse(BaseModel):
    result: list[dict]

# @app.get("/")
# def read_root():
#     return {"message": "API is running. Use the /search endpoint to query."}

@app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=2), k: int = 5):
    """
    Performs a similarity search in the Qdrant vector database.
    """
    db = get_db()
    try:
        docs_with_scores = db.similarity_search_with_score(query=q, k=k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Format the results into the desired JSON structure
    return {
        "result": [
            {
                "score": score,
                "content": doc.page_content.replace('\n', ' ').strip(),
                "metadata": doc.metadata
            }
            for doc, score in docs_with_scores
        ]
    }