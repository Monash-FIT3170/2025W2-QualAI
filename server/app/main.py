from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import asyncio
import os
import json
from datetime import datetime, timedelta
from vosk import Model, KaldiRecognizer
from pathlib import Path

SAMPLE_RATE = 16000
CHUNK_SIZE = 4000

app = FastAPI()


@app.get("/")
async def root():
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


class Transcriber:
    def __init__(self, model_path, recording_path):
        if not os.path.exists(model_path):
            raise ValueError(f"Model path not found: {model_path}")
        self.model = Model(model_path)
        self.recording_path = recording_path

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

    async def transcribe(self, model_path: str):
        rec = KaldiRecognizer(self.model, SAMPLE_RATE)
        rec.SetWords(True)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"File not found: {model_path}")

        transcription = []
        start_time = datetime.now()

        ffmpeg_command = [
            "ffmpeg",
            "-nostdin",
            "-loglevel",
            "quiet",
            "-i",
            self.recording_path,
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
        print (f"an error has occurred")
    

    model_path = "/app/app/vosk-model-en-us-0.22-lgraph"  # Ensure this path is correct
    transcriber = Transcriber(model_path, file_path)

    transcription_raw = await transcriber.transcribe(model_path)
    text_output = " ".join(
        segment["text"]
        for segment in transcription_raw["transcription"]
        if segment["text"].strip()
    )
    return text_output
