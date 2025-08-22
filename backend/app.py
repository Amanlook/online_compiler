"""
FastAPI application factory and setup
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .routes import home, compile_code, analyze_code, analyze_and_compile, health_check


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Online Python Compiler",
        description="A secure online Python compiler using Docker containers",
        version="1.0.0"
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Add routes
    app.get("/", response_class=HTMLResponse)(home)
    app.post("/compile")(compile_code)
    app.post("/analyze")(analyze_code)
    app.post("/analyze-and-compile")(analyze_and_compile)
    app.get("/health")(health_check)

    return app
