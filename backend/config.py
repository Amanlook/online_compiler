"""
Configuration settings for the Online Python Compiler
"""

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
