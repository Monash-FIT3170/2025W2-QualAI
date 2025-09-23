import os
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config(BaseSettings):
    """
    Central location for server settings and data. Also loads values from environment variables.
    """

    # base path
    BASE_PATH: Path = Path(__file__).resolve().parent

    # SQL Databse settings
    DB_PATH: str = str((BASE_PATH / "qualAI.db"))
    DB_PROJECT_TABLE_NAME: str = "project"
    DB_TRANS_TABLE_NAME: str = "transcription"

    # Project settings
    DEFAULT_PROJECT: str = "project_1"

    # CORS settings
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Ollama settings
    OLLAMA_URL: str = "http://ollama:11434/api/generate"
    OLLAMA_MODEL: str = "deepseek-r1:7b"
    OLLAMA_TIMEOUT: float = 300.0

    # Gemini settings
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_API_URL: str = (
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    )

    # Transcription settings
    SAMPLE_RATE: int = 16000
    CHUNK_SIZE: int = 4000
    DIAZARIZATION_TIMEOUT_SECOND: int = 30000
# Create a single instance of the settings to be imported across the application
config = Config()
