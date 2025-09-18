# Multi-stage Docker build for Online Python Compiler with Docker-in-Docker
FROM docker:24-dind AS docker-base

# Install Python and required system dependencies
RUN apk add --no-cache \
    python3 \
    python3-dev \
    py3-pip \
    gcc \
    musl-dev \
    linux-headers \
    supervisor \
    curl \
    bash

# Create symbolic link for python command
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Set up Python virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install .

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/supervisor /var/run/supervisor

# Copy configuration files
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/supervisor-entrypoint.sh /supervisor-entrypoint.sh

# Make scripts executable
RUN chmod +x /entrypoint.sh /supervisor-entrypoint.sh

# Expose the application port
EXPOSE 8888

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8888/health || exit 1

# Use supervisor for production (recommended)
ENTRYPOINT ["/supervisor-entrypoint.sh"]

# Alternative simple entrypoint (uncomment if you prefer single process)
# ENTRYPOINT ["/entrypoint.sh"]