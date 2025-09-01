import httpx
import traceback
from fastapi import HTTPException

from .config import config

async def generate_online(prompt: str) -> dict:
    """
    Generates text using the online Gemini API.

    Args:
        prompt: The augmented prompt to send to the model.

    Returns:
        A dictionary containing the model's response.
    """
    if not config.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured.")

    url = f"{config.GEMINI_API_URL}?key={config.GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=config.OLLAMA_TIMEOUT)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            data = response.json()
            # print("Gemini API response:", data)
            
            # Safely extract the text from the response
            reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return {"response": reply.strip()}
            
    except httpx.HTTPStatusError as e:
        print(f"Gemini API Error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Online mode failed: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred in online mode: {e}")
        raise HTTPException(status_code=500, detail=f"Online mode failed with an unexpected error: {str(e)}")


async def generate_offline(prompt: str) -> dict:
    """
    Generates text using the offline Ollama service.

    Args:
        prompt: The augmented prompt to send to the model.

    Returns:
        A dictionary containing the model's response.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.OLLAMA_URL,
                json={
                    "model": config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=config.OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            
            json_response = response.json()
            return {"response": json_response.get("response", "No 'response' field in Ollama reply")}
            
    except httpx.HTTPStatusError as e:
        print(f"OLLAMA Error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Offline mode failed: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred in offline mode: {e}")
        raise HTTPException(status_code=500, detail=f"Offline mode failed with an unexpected error: {str(e)}")