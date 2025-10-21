from app.config import config

from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str
    project: int
    mode: str = "offline"  # default = offline
    template: str = "default"  # Analysis mode
