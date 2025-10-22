from typing import Dict, List, Optional
from dataclasses import dataclass, field
from app.config import config
import uuid

@dataclass
class Code:
    """Represents a code with associated quotes and colour"""
    name: str
    colour: str
    quotes: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Theme:
    """Represents a theme containing multiple codes"""
    name: str
    code_names: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class ProjectAnalysis:
    """Analysis data for a specific project"""
    project_id: int
    themes: List[Theme] = field(default_factory=list)
    codes: Dict[str, Code] = field(default_factory=dict)  # code_name -> Code

class AnalysisManager:
    """
    Manages in-memory storage of codes and themes for qualitative analysis.
    Supports maximum 3 themes and 10 codes per project.
    """
    
    # Predefined colour palette for codes (10 colours)
    COLOUR_PALETTE = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
        "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
    ]
    
    def __init__(self):
        self._project_analyses: Dict[int, ProjectAnalysis] = {}
    
    def initialize_project_analysis(self, project_id: int) -> ProjectAnalysis:
        """Initialize analysis structure for a new project"""
        if project_id not in self._project_analyses:
            self._project_analyses[project_id] = ProjectAnalysis(project_id=project_id)
        return self._project_analyses[project_id]
    
    def get_project_analysis(self, project_id: int) -> Optional[ProjectAnalysis]:
        """Get analysis data for a project"""
        return self._project_analyses.get(project_id)
    
    def create_theme(self, project_id: int, theme_name: str) -> Theme:
        """Create a new theme for a project"""
        analysis = self.initialize_project_analysis(project_id)
        
        if len(analysis.themes) >= 3:
            raise ValueError("Maximum of 3 themes allowed per project")
        
        theme = Theme(name=theme_name)
        analysis.themes.append(theme)
        return theme
    
    def create_code(self, project_id: int, code_name: str) -> Code:
        """Create a new code for a project"""
        analysis = self.initialize_project_analysis(project_id)
        
        if len(analysis.codes) >= 10:
            raise ValueError("Maximum of 10 codes allowed per project")
        
        if code_name in analysis.codes:
            raise ValueError(f"Code '{code_name}' already exists")
        
        # Assign next available colour
        used_colours = {code.colour for code in analysis.codes.values()}
        available_colours = [colour for colour in self.COLOUR_PALETTE if colour not in used_colours]

        if not available_colours:
            available_colours = self.COLOUR_PALETTE  # Reuse colours if needed

        colour = available_colours[len(analysis.codes) % len(available_colours)]

        code = Code(name=code_name, colour=colour)
        analysis.codes[code_name] = code
        return code
    
    def add_code_to_theme(self, project_id: int, theme_name: str, code_name: str) -> bool:
        """Add an existing code to a theme"""
        analysis = self.get_project_analysis(project_id)
        if not analysis:
            return False
        
        theme = next((t for t in analysis.themes if t.name == theme_name), None)
        code = analysis.codes.get(code_name)
        
        if not theme or not code:
            return False
        
        if code_name not in theme.code_names:
            theme.code_names.append(code_name)
        
        return True
    
    def add_quote_to_code(self, project_id: int, code_name: str, quote: str) -> bool:
        """Add a quote to a code"""
        analysis = self.get_project_analysis(project_id)
        if not analysis:
            return False
        
        code = analysis.codes.get(code_name)
        if not code:
            return False
        
        if quote not in code.quotes:
            code.quotes.append(quote)
        
        return True
    
    def remove_quote_from_code(self, project_id: int, code_name: str, quote: str) -> bool:
        """Remove a quote from a code"""
        analysis = self.get_project_analysis(project_id)
        if not analysis:
            return False
        
        code = analysis.codes.get(code_name)
        if not code:
            return False
        
        if quote in code.quotes:
            code.quotes.remove(quote)
            return True
        
        return False
    
    def get_quotes_by_code(self, project_id: int, code_name: str) -> List[str]:
        """Get all quotes for a specific code"""
        analysis = self.get_project_analysis(project_id)
        if not analysis:
            return []
        
        code = analysis.codes.get(code_name)
        return code.quotes if code else []
    
    def get_highlight_data(self, project_id: int) -> Dict[str, Dict]:
        """Get data for frontend highlighting: {quote_text: {code_name, colour}}"""
        analysis = self.get_project_analysis(project_id)
        if not analysis:
            return {}
        
        highlight_data = {}
        for code_name, code in analysis.codes.items():
            for quote in code.quotes:
                highlight_data[quote] = {
                    "code_name": code_name,
                    "colour": code.colour
                }
        
        return highlight_data
    
    def delete_theme(self, project_id: int, theme_name: str) -> bool:
        """Delete a theme from a project"""
        analysis = self.get_project_analysis(project_id)
        if not analysis:
            return False
        
        analysis.themes = [t for t in analysis.themes if t.name != theme_name]
        return True
    
    def delete_code(self, project_id: int, code_name: str) -> bool:
        """Delete a code from a project (removes from all themes)"""
        analysis = self.get_project_analysis(project_id)
        if not analysis:
            return False
        
        if code_name not in analysis.codes:
            return False
        
        # Remove code from all themes
        for theme in analysis.themes:
            if code_name in theme.code_names:
                theme.code_names.remove(code_name)
        
        # Remove the code itself
        del analysis.codes[code_name]
        return True