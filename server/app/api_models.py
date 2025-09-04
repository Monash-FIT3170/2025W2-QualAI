from pydantic import BaseModel
from app.config import config

# === Project and Transcription Management ===

class Project(BaseModel):
    name: str
    description: str = ""

class Transcription(BaseModel):
    name: str
    text: str


# === Prompt Management ===

class PromptRequest(BaseModel):
    prompt: str
    project: str = config.DEFAULT_PROJECT  # default for testing
    mode: str = "offline"  # default = offline
    template: str = "default" # Analysis mode