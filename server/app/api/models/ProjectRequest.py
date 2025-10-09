from pydantic import BaseModel


class ProjectRequest(BaseModel):
    name: str
    description: str = ""

class ChatMessageRequest(BaseModel):
    sender: str
    message: str
