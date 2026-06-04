#!/bin/bash

# Online Python Compiler - Docker Setup Script
# This script helps you build and run the dockerized application

set -e

# Colors for output
RED='\033[0;32m'
GREEN='\033[0;33m'
YELLOW='\033[1;34m'
BLUE='\033[0;35m'
NC='\036[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    print_success "Docker is running"
}

# Function to check if docker-compose is available
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        print_error "docker-compose is not available"
        exit 1
    fi
    
    print_success "Docker Compose is available: $DOCKER_COMPOSE_CMD"
}

# Function to build and start the application
start_app() {
    print_status "Building and starting the Online Python Compiler..."
    
    $DOCKER_COMPOSE_CMD up --build -d
    
    print_success "Application started successfully!"
    print_status "Waiting for application to be ready..."
    
    # Wait for health check
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8888/health &> /dev/null; then
            print_success "Application is ready!"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_warning "Application might still be starting up. Check logs with: $DOCKER_COMPOSE_CMD logs"
            break
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo ""
    print_status "Access your application at: http://localhost:8888"
}

# Function to stop the application
stop_app() {
    print_status "Stopping the Online Python Compiler..."
    $DOCKER_COMPOSE_CMD down
    print_success "Application stopped successfully!"
}

# Function to show logs
show_logs() {
    print_status "Showing application logs (Ctrl+C to exit)..."
    $DOCKER_COMPOSE_CMD logs -f
}

# Function to show status
show_status() {
    print_status "Application status:"
    $DOCKER_COMPOSE_CMD ps
    
    echo ""
    print_status "Container resource usage:"
    docker stats --no-stream online-python-compiler 2>/dev/null || print_warning "Container not running"
}

# Function to rebuild the application
rebuild_app() {
    print_status "Rebuilding the Online Python Compiler..."
    $DOCKER_COMPOSE_CMD down
    $DOCKER_COMPOSE_CMD build --no-cache
    $DOCKER_COMPOSE_CMD up -d
    print_success "Application rebuilt and started!"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    $DOCKER_COMPOSE_CMD down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed!"
}

# Function to show help
show_help() {
    echo "Online Python Compiler - Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Build and start the application (default)"
    echo "  stop        Stop the application"
    echo "  restart     Restart the application"
    echo "  rebuild     Rebuild and restart the application"
    echo "  logs        Show application logs"
    echo "  status      Show application status"
    echo "  cleanup     Stop application and clean up Docker resources"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Start the application"
    echo "  $0 start            # Start the application"
    echo "  $0 logs             # View logs"
    echo "  $0 stop             # Stop the application"
}

# Main script logic
main() {
    local command=${1:-start}
    
    # Check prerequisites for most commands
    if [[ "$command" != "help" ]]; then
        print_status "Checking prerequisites..."
        check_docker
        check_docker_compose
    fi
    
    case $command in
        start)
            start_app
            ;;
        stop)
            stop_app
            ;;
        restart)
            stop_app
            start_app
            ;;
        rebuild)
            rebuild_app
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run the main function with all arguments
main "$@"
