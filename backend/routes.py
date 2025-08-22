"""
FastAPI routes for the Online Python Compiler
"""

from fastapi import Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from .compiler import PythonCompiler
from .llm_analyzer import LLMCodeAnalyzer

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize the compiler and analyzer
compiler = PythonCompiler()
analyzer = LLMCodeAnalyzer()


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


async def analyze_code(code: str = Form(...)):
    """
    Analyze Python code for security, syntax, and quality issues using LLM
    
    Args:
        code: Python code to analyze
        
    Returns:
        JSON response with analysis result including suggestions and fixes
    """
    try:
        result = await analyzer.analyze_code(code)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "security_issues": [],
                "syntax_errors": [],
                "suggestions": [],
                "is_safe": True,
                "error": f"Analysis error: {str(e)}"
            },
            status_code=500
        )


async def analyze_and_compile(code: str = Form(...)):
    """
    First analyze the code, then compile if safe
    
    Args:
        code: Python code to analyze and compile
        
    Returns:
        JSON response with analysis and execution results
    """
    try:
        # First analyze the code
        analysis = await analyzer.analyze_code(code)
        
        # If there are critical security issues, don't execute
        has_critical_issues = any(
            issue.get("severity") == "high" 
            for issue in analysis.get("security_issues", [])
        )
        
        if has_critical_issues or not analysis.get("is_safe", True):
            return JSONResponse(content={
                "analysis": analysis,
                "execution": {
                    "success": False,
                    "output": "",
                    "error": "Code execution blocked due to security concerns"
                }
            })
        
        # If safe, execute the code
        execution = await compiler.execute_code(code)
        
        return JSONResponse(content={
            "analysis": analysis,
            "execution": execution
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "analysis": {
                    "success": False,
                    "error": f"Analysis error: {str(e)}"
                },
                "execution": {
                    "success": False,
                    "output": "",
                    "error": f"Server error: {str(e)}"
                }
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
