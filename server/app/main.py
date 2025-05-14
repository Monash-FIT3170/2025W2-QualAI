from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import subprocess
import os
import json
from datetime import datetime, timedelta

from vosk import Model, KaldiRecognizer

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
        <p>Example using curl:</p>
        <pre><code>
        Go to http://127.0.0.1:8000/transcribe/
        </code></pre>
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
            "text": data.get("text", "")
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
            model_path,
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "1",
            "-f",
            "s16le",
            "-"
        ]

        process = await subprocess.create_subprocess_exec(
            *ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE  # Capture stderr for potential errors
        )

        while True:
            if process.stdout is None:
                break
            data = await process.stdout.read(CHUNK_SIZE)
            if not data:
                break
            if rec.AcceptWaveform(data):
                transcription.append(self.fmt(rec.Result()))

        transcription.append(self.fmt(rec.FinalResult()))

        return{"transcription" : transcription}


model_path = "/app/app/vosk-model-en-us-0.22-lgraph"  # Ensure this path is correct
recording_path = "/app/app/bruh.mp3"
transcriber = Transcriber(model_path, recording_path)


@app.post("/transcribe/")
async def transcribe_audio():
    transcription_result = await transcriber.transcribe(transcriber.recording_path)
    return transcription_result
