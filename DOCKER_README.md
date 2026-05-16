# Docker Setup for Online Python Compiler

This guide explains how to run the Online Python Compiler using Docker-in-Docker (DinD), making it completely self-contained without dependencies on the host Docker daemon.

## Architecture

The application uses Docker-in-Docker to provide complete isolation:

- **Host**: Runs the main application container
- **Container**: Contains both the FastAPI application and an internal Docker daemon
- **Code Execution**: User code runs in nested Docker containers within the main container

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Open your browser to `http://localhost:8888`
   - Use the web interface to compile and run Python code

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t online-python-compiler .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name online-python-compiler \
     --privileged \
     -p 8888:8888 \
     -v docker-data:/var/lib/docker \
     online-python-compiler
   ```

3. **Stop and remove:**
   ```bash
   docker stop online-python-compiler
   docker rm online-python-compiler
   ```

## Configuration

### Environment Variables

You can customize the application behavior using environment variables:

#### Application Settings
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `DEBUG`: Debug mode (default: `false`)

#### Docker Execution Settings
- `DOCKER_IMAGE`: Python image for code execution (default: `python:3.11-alpine`)
- `TIMEOUT`: Code execution timeout in seconds (default: `10`)
- `MEMORY_LIMIT`: Memory limit for code execution (default: `128m`)
- `CPU_LIMIT`: CPU limit for code execution (default: `0.5`)

#### Security Settings
- `MAX_OUTPUT_SIZE`: Maximum output size in bytes (default: `1048576`)
- `TEMP_DIR_SIZE`: Temporary directory size (default: `10m`)

#### LLM Integration (Optional)
- `LLM_PROVIDER`: LLM provider (`perplexity`, `openai`, `anthropic`, `ollama`)
- `PERPLEXITY_API_KEY`: Perplexity API key
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `LLM_MODEL`: Model name
- `LLM_MAX_TOKENS`: Maximum tokens for LLM responses
- `LLM_TIMEOUT`: LLM request timeout

### Example with Environment Variables

```bash
docker run -d \
  --name online-python-compiler \
  --privileged \
  -p 8888:8888 \
  -e HOST=0.0.0.0 \
  -e PORT=8888 \
  -e DEBUG=false \
  -e TIMEOUT=15 \
  -e MEMORY_LIMIT=256m \
  -e PERPLEXITY_API_KEY=your_api_key_here \
  -v docker-data:/var/lib/docker \
  online-python-compiler
```

## Security Features

The application implements multiple security layers:

### Container Security
- **Privileged mode**: Required only for Docker-in-Docker functionality
- **Resource limits**: CPU and memory constraints for the main container
- **Volume isolation**: Docker data stored in named volumes

### Code Execution Security
- **Isolated containers**: Each code execution runs in a separate container
- **No network access**: Code execution containers have no internet access
- **Read-only filesystem**: Containers use read-only root filesystem
- **Non-root user**: Code runs as `nobody` user
- **Resource limits**: Strict CPU, memory, and time limits
- **Capability dropping**: All Linux capabilities dropped
- **Security options**: Additional security restrictions applied

## Monitoring and Logs

### Health Check
The container includes a health check endpoint:
```bash
curl http://localhost:8888/health
```

### Viewing Logs
```bash
# View application logs
docker-compose logs online-compiler

# Follow logs in real-time
docker-compose logs -f online-compiler

# View specific service logs (when using supervisor)
docker exec online-python-compiler tail -f /var/log/supervisor/python-app.log
docker exec online-python-compiler tail -f /var/log/supervisor/dockerd.log
```

### Container Statistics
```bash
# View resource usage
docker stats online-python-compiler

# View running processes inside container
docker exec online-python-compiler ps aux
```

## Persistence

### Docker Volume
- **Purpose**: Stores Docker daemon data and pulled images
- **Location**: `/var/lib/docker` inside container
- **Benefit**: Avoids re-downloading Python images on container restart

### Log Persistence (Optional)
Mount logs directory for easier debugging:
```yaml
volumes:
  - ./logs:/var/log/supervisor
```

## Troubleshooting

### Common Issues

1. **Permission denied errors**
   - Ensure the container runs with `--privileged` flag
   - Check that Docker daemon is running inside the container

2. **Container fails to start**
   - Check logs: `docker-compose logs online-compiler`
   - Verify system resources are available
   - Ensure port 8888 is not already in use

3. **Code execution timeouts**
   - Increase `TIMEOUT` environment variable
   - Check Docker daemon status inside container
   - Monitor resource usage

4. **Out of memory errors**
   - Increase container memory limits in docker-compose.yml
   - Adjust `MEMORY_LIMIT` for code execution
   - Monitor memory usage with `docker stats`

### Debug Commands

```bash
# Enter the container
docker exec -it online-python-compiler /bin/bash

# Check Docker daemon status inside container
docker exec online-python-compiler docker info

# Check application status
docker exec online-python-compiler curl -f http://localhost:8888/health

# View supervisor status
docker exec online-python-compiler supervisorctl status

# Restart services inside container
docker exec online-python-compiler supervisorctl restart python-app
docker exec online-python-compiler supervisorctl restart dockerd
```

## Development

### Building for Development
```bash
# Build with development settings
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Running Tests
```bash
# Run tests inside container
docker exec online-python-compiler python -m pytest

# Run tests with volume mount for development
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  online-python-compiler \
  python -m pytest
```

## Production Deployment

### Recommendations

1. **Use specific image tags**: Avoid `latest` tags in production
2. **Set resource limits**: Configure appropriate CPU and memory limits
3. **Enable logging**: Use proper log drivers and external log aggregation
4. **Monitor health**: Implement proper health checks and monitoring
5. **Backup volumes**: Regular backup of Docker data volume
6. **Security scanning**: Regular security scans of the container images

### Example Production Setup
```yaml
version: '3.8'
services:
  online-compiler:
    image: online-python-compiler:1.0.0
    restart: always
    privileged: true
    ports:
      - "8888:8888"
    environment:
      - DEBUG=false
      - TIMEOUT=10
    volumes:
      - docker-data:/var/lib/docker
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## API Documentation

Once running, access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8888/docs`
- **ReDoc**: `http://localhost:8888/redoc`

## Support

For issues and questions:
1. Check the logs for error messages
2. Verify configuration and environment variables
3. Test with minimal configuration first
4. Use debug commands to inspect container state