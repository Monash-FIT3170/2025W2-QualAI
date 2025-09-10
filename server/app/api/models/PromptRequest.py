from app.config import config

from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str
    project: str = config.DEFAULT_PROJECT  # default for testing
    mode: str = "offline"  # default = offline
    template: str = "default"  # Analysis mode
