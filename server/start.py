# ./server/start.py
from os import execvp

def start_server():
    """Starts the Uvicorn server."""
    print("--- 🚀 Starting FastAPI server... ---")
    # Use os.execvp to replace the current process with Uvicorn
    # This is important for correct signal handling in Docker
    execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--lifespan", "on"])

if __name__ == "__main__":
    start_server()