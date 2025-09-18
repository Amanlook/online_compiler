#!/bin/bash
set -e

# Start Docker daemon in background
echo "Starting Docker daemon..."
dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2376 --storage-driver=overlay2 &

# Wait for Docker daemon to be ready
echo "Waiting for Docker daemon to be ready..."
timeout 30 sh -c 'until docker info >/dev/null 2>&1; do sleep 1; done'

# Pull the Python image that will be used for code execution
echo "Pulling Python execution image..."
docker pull python:3.11-alpine

# Start the FastAPI application
echo "Starting FastAPI application..."
exec /opt/venv/bin/python main.py