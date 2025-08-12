"""
Online Python Compiler - Main Entry Point
"""

import uvicorn
from backend.app import create_app
from backend.config import HOST, PORT, DEBUG

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info"
    )
