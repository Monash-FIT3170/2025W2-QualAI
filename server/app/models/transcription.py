from pydantic import BaseModel

class Transcription(BaseModel):
    name: str
    text: str
