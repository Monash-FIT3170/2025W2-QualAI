from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import traceback

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
    return {"message": "Hello World"}

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
