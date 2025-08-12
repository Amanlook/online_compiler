"""
FastAPI routes for the Online Python Compiler
"""

from fastapi import Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from .compiler import PythonCompiler

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize the compiler
compiler = PythonCompiler()


def home(request: Request):
    """Serve the main page with the code editor"""
    return templates.TemplateResponse("index.html", {"request": request})


async def compile_code(code: str = Form(...)):
    """
    Compile and execute Python code safely in Docker container
    
    Args:
        code: Python code to execute
        
    Returns:
        JSON response with execution result
    """
    try:
        result = await compiler.execute_code(code)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "output": "",
                "error": f"Server error: {str(e)}"
            },
            status_code=500
        )


def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Python compiler is running",
        "docker_image": compiler.docker_image,
        "timeout": compiler.timeout
    }
