from fastapi import APIRouter, Request, HTTPException
from app.service.analysis_manager import AnalysisManager
from app.api.analysis_models import (
    CodeCreateRequest, ThemeCreateRequest, AddCodeToThemeRequest,
    AddQuoteRequest, ProjectAnalysisResponse
)

analysis_router = APIRouter()

@analysis_router.get("/projects/{project_id}/analysis")
def get_project_analysis(request: Request, project_id: int) -> ProjectAnalysisResponse:
    """
    Get complete analysis data (themes, codes, quotes) for a project
    """
    analysis_manager: AnalysisManager = request.app.state.analysis_manager
    analysis = analysis_manager.get_project_analysis(project_id)
    
    if not analysis:
        # Return empty analysis structure
        return ProjectAnalysisResponse(
            project_id=project_id,
            themes=[],
            codes={},
            highlight_data={}
        )
    
    # Convert to response format
    theme_responses = []
    for theme in analysis.themes:
        theme_responses.append({
            "name": theme.name,
            "code_names": theme.code_names
        })
    
    code_responses = {}
    for code_name, code in analysis.codes.items():
        code_responses[code_name] = {
            "name": code.name,
            "colour": code.colour,
            "quotes": code.quotes
        }
    
    highlight_data = analysis_manager.get_highlight_data(project_id)
    
    return ProjectAnalysisResponse(
        project_id=project_id,
        themes=theme_responses,
        codes=code_responses,
        highlight_data=highlight_data
    )

@analysis_router.post("/projects/{project_id}/themes")
def create_theme(request: Request, project_id: int, payload: ThemeCreateRequest):
    """
    Create a new theme for a project (max 3 themes)
    """
    analysis_manager: AnalysisManager = request.app.state.analysis_manager
    
    try:
        theme = analysis_manager.create_theme(project_id, payload.name)
        return {"theme": theme.name, "message": "Theme created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create theme: {str(e)}")

@analysis_router.post("/projects/{project_id}/codes")
def create_code(request: Request, project_id: int, payload: CodeCreateRequest):
    """
    Create a new code for a project (max 10 codes)
    """
    analysis_manager: AnalysisManager = request.app.state.analysis_manager
    
    try:
        code = analysis_manager.create_code(project_id, payload.name)
        return {
            "code": code.name, 
            "colour": code.colour,
            "message": "Code created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create code: {str(e)}")

@analysis_router.post("/projects/{project_id}/themes/{theme_name}/codes")
def add_code_to_theme(
    request: Request, 
    project_id: int, 
    theme_name: str, 
    payload: AddCodeToThemeRequest
):
    """
    Add an existing code to a theme
    """
    analysis_manager: AnalysisManager = request.app.state.analysis_manager
    
    success = analysis_manager.add_code_to_theme(project_id, theme_name, payload.code_name)
    
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Theme or code not found"
        )
    
    return {"message": f"Code '{payload.code_name}' added to theme '{theme_name}'"}

@analysis_router.post("/projects/{project_id}/codes/{code_name}/quotes")
def add_quote_to_code(
    request: Request,
    project_id: int,
    code_name: str,
    payload: AddQuoteRequest
):
    """
    Add a quote to a code for highlighting
    """
    analysis_manager: AnalysisManager = request.app.state.analysis_manager
    
    success = analysis_manager.add_quote_to_code(project_id, code_name, payload.quote)
    
    if not success:
        raise HTTPException(status_code=404, detail="Code not found")
    
    return {"message": f"Quote added to code '{code_name}'"}

@analysis_router.get("/projects/{project_id}/highlighting")
def get_highlighting_data(request: Request, project_id: int):
    """
    Get highlighting data for frontend: {quote_text: {code_name, colour}}
    """
    analysis_manager: AnalysisManager = request.app.state.analysis_manager
    highlight_data = analysis_manager.get_highlight_data(project_id)
    
    return {"project_id": project_id, "highlighting": highlight_data}

@analysis_router.delete("/projects/{project_id}/themes/{theme_name}")
def delete_theme(request: Request, project_id: int, theme_name: str):
    """
    Delete a theme from a project
    """
    analysis_manager: AnalysisManager = request.app.state.analysis_manager
    
    success = analysis_manager.delete_theme(project_id, theme_name)
    
    if not success:
        raise HTTPException(status_code=404, detail="Theme not found")
    
    return {"message": f"Theme '{theme_name}' deleted successfully"}

@analysis_router.delete("/projects/{project_id}/codes/{code_name}")
def delete_code(request: Request, project_id: int, code_name: str):
    """
    Delete a code from a project (removes from all themes)
    """
    analysis_manager: AnalysisManager = request.app.state.analysis_manager
    
    success = analysis_manager.delete_code(project_id, code_name)
    
    if not success:
        raise HTTPException(status_code=404, detail="Code not found")
    
    return {"message": f"Code '{code_name}' deleted successfully"}