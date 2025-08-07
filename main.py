import sys
import tempfile
import os
from typing import Dict, Any
import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Online Python Compiler", version="1.0.0")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


class PythonCompiler:
    """A simple Python code compiler/executor"""
    
    def __init__(self):
        self.timeout = 10  # 10 seconds timeout for code execution
    
    async def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code safely and return the result
        """
        if not code.strip():
            return {
                "success": False,
                "output": "",
                "error": "No code provided"
            }
        
        # Create a temporary file to store the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Execute the code using subprocess
            result = await asyncio.create_subprocess_exec(
                sys.executable, temp_file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024 * 1024  # 1MB limit for output
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(), 
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                result.kill()
                await result.wait()
                return {
                    "success": False,
                    "output": "",
                    "error": f"Code execution timed out after {self.timeout} seconds"
                }
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            # Decode the output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": stdout_text,
                    "error": ""
                }
            else:
                return {
                    "success": False,
                    "output": stdout_text,
                    "error": stderr_text
                }
                
        except Exception as e:
            # Clean up the temporary file in case of exception
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}"
            }


# Initialize the compiler
compiler = PythonCompiler()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main page with the code editor"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/compile")
async def compile_code(code: str = Form(...)):
    """
    Compile and execute Python code
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Python compiler is running"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8888,
        reload=True,
        log_level="info"
    )
