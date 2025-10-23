from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    sender: str
    message: str
