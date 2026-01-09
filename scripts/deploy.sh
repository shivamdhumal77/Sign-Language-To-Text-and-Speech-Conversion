#!/bin/bash

# Sign Language Recognition App Deployment Script
# This script handles the complete deployment process

set -e

# Configuration
REGISTRY="ghcr.io"
IMAGE_NAME="sign-language-to-text-and-speech-conversion"
NAMESPACE="sign-language-app"
KUBECTL="kubectl"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if cluster is accessible
    if ! $KUBECTL cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    log_info "Prerequisites check passed."
}

# Build and push Docker image
build_and_push() {
    local tag=${1:-latest}
    log_info "Building Docker image with tag: $tag"
    
    # Build image
    docker build -f ./docker/app.Dockerfile -t $REGISTRY/$IMAGE_NAME:$tag .
    
    # Push image
    log_info "Pushing Docker image to registry..."
    docker push $REGISTRY/$IMAGE_NAME:$tag
    
    log_info "Docker image built and pushed successfully."
}

# Deploy to Kubernetes
deploy_k8s() {
    local environment=${1:-staging}
    log_info "Deploying to Kubernetes namespace: $NAMESPACE"
    
    # Create namespace
    $KUBECTL apply -f k8s/namespace.yml
    
    # Apply configurations
    $KUBECTL apply -f k8s/configmap.yml -n $NAMESPACE
    
    # Update deployment with correct image
    if [ "$environment" = "production" ]; then
        sed 's|ghcr.io/yourusername/sign-language-to-text-and-speech-conversion:latest|'$REGISTRY'/'$IMAGE_NAME':main|g' k8s/deployment.yml | $KUBECTL apply -f - -n $NAMESPACE
    else
        sed 's|ghcr.io/yourusername/sign-language-to-text-and-speech-conversion:latest|'$REGISTRY'/'$IMAGE_NAME':develop|g' k8s/deployment.yml | $KUBECTL apply -f - -n $NAMESPACE
    fi
    
    # Apply other resources
    $KUBECTL apply -f k8s/service.yml -n $NAMESPACE
    $KUBECTL apply -f k8s/hpa.yml -n $NAMESPACE
    
    # Apply ingress only for production
    if [ "$environment" = "production" ]; then
        $KUBECTL apply -f k8s/ingress.yml -n $NAMESPACE
    fi
    
    log_info "Kubernetes resources deployed successfully."
}

# Wait for deployment to be ready
wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."
    
    $KUBECTL wait --for=condition=available --timeout=300s deployment/sign-language-app -n $NAMESPACE
    
    log_info "Deployment is ready!"
}

# Show deployment status
show_status() {
    log_info "Deployment status:"
    $KUBECTL get pods -n $NAMESPACE
    $KUBECTL get services -n $NAMESPACE
    $KUBECTL get ingress -n $NAMESPACE 2>/dev/null || log_warn "Ingress not found or not deployed"
}

# Cleanup function
cleanup() {
    log_warn "Cleaning up..."
    # Add any cleanup logic here
}

# Main deployment function
main() {
    local environment=${1:-staging}
    local tag=${2:-latest}
    
    log_info "Starting deployment for environment: $environment"
    
    # Set up trap for cleanup
    trap cleanup EXIT
    
    # Check prerequisites
    check_prerequisites
    
    # Build and push image
    build_and_push $tag
    
    # Deploy to Kubernetes
    deploy_k8s $environment
    
    # Wait for deployment
    wait_for_deployment
    
    # Show status
    show_status
    
    log_info "Deployment completed successfully!"
    
    if [ "$environment" = "production" ]; then
        log_info "Production deployment is live. Monitor the application closely."
    else
        log_info "Staging deployment is ready for testing."
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [ENVIRONMENT] [TAG]"
    echo ""
    echo "ENVIRONMENT: staging (default) or production"
    echo "TAG: Docker image tag (default: latest)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy to staging with latest tag"
    echo "  $0 production         # Deploy to production with latest tag"
    echo "  $0 staging v1.0.0     # Deploy to staging with v1.0.0 tag"
    echo "  $0 production main    # Deploy to production with main tag"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            main "$@"
            ;;
    esac
fi
