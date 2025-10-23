from pydantic import BaseModel


class HighlighterRequest(BaseModel):
    label: str
    colour: str
    weight: int
