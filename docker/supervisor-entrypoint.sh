#!/bin/bash
set -e

# Start Docker daemon in background first
echo "Starting Docker daemon in background..."
dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2376 --storage-driver=overlay2 &

# Wait for Docker daemon to be ready
echo "Waiting for Docker daemon to be ready..."
timeout 60 sh -c 'until docker info >/dev/null 2>&1; do sleep 1; done'

# Pre-pull the Python image for code execution
echo "Pulling Python execution image..."
docker pull python:3.11-alpine

# Now start supervisor to manage both services properly
echo "Starting supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf