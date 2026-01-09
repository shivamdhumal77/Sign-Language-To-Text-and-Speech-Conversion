#!/bin/bash

# Local Deployment Script
# This script handles local development and testing deployment

set -e

# Configuration
PROJECT_NAME="sign-language-app"
CONTAINER_NAME="sign-language-app-local"
PORT=5000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Stop existing container
stop_container() {
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Stopping existing container..."
        docker stop $CONTAINER_NAME
    fi
    
    if docker ps -aq -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Removing existing container..."
        docker rm $CONTAINER_NAME
    fi
}

# Build and run container
run_container() {
    local environment=${1:-"development"}
    
    log_info "Building Docker image..."
    docker build -f ./docker/app.Dockerfile -t $PROJECT_NAME:latest .
    
    log_info "Starting container on port $PORT..."
    
    # Check if camera device exists (Linux/Mac)
    local camera_device=""
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -e "/dev/video0" ]; then
            camera_device="--device /dev/video0:/dev/video0"
            log_info "Found camera device: /dev/video0"
        fi
    fi
    
    # Run container with appropriate settings
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:5000 \
        -e FLASK_HOST=0.0.0.0 \
        -e FLASK_PORT=5000 \
        -e FLASK_DEBUG=true \
        -e LOG_LEVEL=DEBUG \
        -e CAMERA_INDEX=0 \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/sign_language_AZ_CNN.h5:/app/sign_language_AZ_CNN.h5:ro \
        -v $(pwd)/templates:/app/templates:ro \
        $camera_device \
        $PROJECT_NAME:latest
    
    log_info "Container started successfully!"
}

# Wait for container to be ready
wait_for_container() {
    log_info "Waiting for application to start..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:$PORT/health &> /dev/null; then
            log_info "Application is ready!"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: Waiting for application..."
        sleep 2
        ((attempt++))
    done
    
    log_error "Application failed to start within expected time."
    return 1
}

# Show container logs
show_logs() {
    log_info "Container logs:"
    docker logs -f $CONTAINER_NAME
}

# Test application
test_app() {
    log_info "Testing application endpoints..."
    
    # Test health endpoint
    if curl -f http://localhost:$PORT/health; then
        log_info "✓ Health check passed"
    else
        log_error "✗ Health check failed"
        return 1
    fi
    
    # Test main endpoint
    if curl -f http://localhost:$PORT/; then
        log_info "✓ Main endpoint accessible"
    else
        log_error "✗ Main endpoint failed"
        return 1
    fi
    
    log_info "All tests passed!"
}

# Open browser
open_browser() {
    log_info "Opening browser..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:$PORT
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:$PORT
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        start http://localhost:$PORT
    else
        log_warn "Could not detect OS. Please open http://localhost:$PORT manually"
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    stop_container
}

# Main function
main() {
    local command=${1:-"start"}
    
    case $command in
        "start")
            log_info "Starting local deployment..."
            stop_container
            run_container
            if wait_for_container; then
                test_app
                open_browser
                log_info "Local deployment is ready at http://localhost:$PORT"
                log_info "Run '$0 logs' to see application logs"
                log_info "Run '$0 stop' to stop the application"
            else
                log_error "Failed to start application"
                show_logs
                exit 1
            fi
            ;;
        "stop")
            stop_container
            log_info "Application stopped."
            ;;
        "restart")
            stop_container
            run_container
            wait_for_container
            log_info "Application restarted."
            ;;
        "logs")
            show_logs
            ;;
        "test")
            test_app
            ;;
        "status")
            if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
                log_info "Application is running"
                docker ps -f name=$CONTAINER_NAME
            else
                log_warn "Application is not running"
            fi
            ;;
        "cleanup")
            cleanup
            docker rmi $PROJECT_NAME:latest 2>/dev/null || true
            log_info "Cleanup completed."
            ;;
        -h|--help)
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  start     Start the application (default)"
            echo "  stop      Stop the application"
            echo "  restart   Restart the application"
            echo "  logs      Show application logs"
            echo "  test      Test application endpoints"
            echo "  status    Show application status"
            echo "  cleanup   Stop and remove all resources"
            echo "  help      Show this help message"
            ;;
        *)
            log_error "Unknown command: $command"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Set up trap for cleanup
trap cleanup EXIT

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
