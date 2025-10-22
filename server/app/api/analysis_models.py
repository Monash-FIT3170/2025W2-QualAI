from pydantic import BaseModel
from typing import List, Dict, Optional

class CodeCreateRequest(BaseModel):
    name: str

class ThemeCreateRequest(BaseModel):
    name: str

class AddCodeToThemeRequest(BaseModel):
    code_name: str

class AddQuoteRequest(BaseModel):
    quote: str

class CodeResponse(BaseModel):
    name: str
    colour: str
    quotes: List[str]

class ThemeResponse(BaseModel):
    name: str
    code_names: List[str]

class ProjectAnalysisResponse(BaseModel):
    project_id: int
    themes: List[ThemeResponse]
    codes: Dict[str, CodeResponse]
    highlight_data: Dict[str, Dict]  # For frontend highlighting

class HighlightResponse(BaseModel):
    quote: str
    code_name: str
    colour: str