"""
Configuration settings for the Online Python Compiler
"""
import os

# Docker Configuration
DOCKER_IMAGE = "python:3.11-alpine"
TIMEOUT = 10  # seconds
MEMORY_LIMIT = "128m"
CPU_LIMIT = "0.5"

# Server Configuration
HOST = "0.0.0.0"
PORT = 8888
DEBUG = True

# Security Configuration
MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB
TEMP_DIR_SIZE = "10m"

# Rate Limiting (future use)
MAX_REQUESTS_PER_MINUTE = 60

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "github")  # github, perplexity, openai, anthropic, or ollama
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # GitHub Models API token
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_BASE_URL = os.getenv("PERPLEXITY_BASE_URL", "https://api.perplexity.ai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")  # GitHub Models default
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "10"))  # seconds
