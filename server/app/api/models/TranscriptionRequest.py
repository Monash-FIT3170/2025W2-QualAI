from pydantic import BaseModel


class TranscriptionRequest(BaseModel):
    name: str
    text: str
