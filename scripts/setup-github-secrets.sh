#!/bin/bash

# Setup GitHub Secrets for Deployment
# This script helps set up necessary secrets in GitHub repository

set -e

# Configuration
REPO_OWNER=${1:-"yourusername"}
REPO_NAME=${2:-"Sign-Language-To-Text-and-Speech-Conversion"}

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

# Check if gh CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed. Please install it first:"
        echo "  macOS: brew install gh"
        echo "  Ubuntu: sudo apt install gh"
        echo "  Windows: winget install GitHub.cli"
        exit 1
    fi
    
    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI is not authenticated. Please run: gh auth login"
        exit 1
    fi
    
    log_info "GitHub CLI is ready."
}

# Setup container registry secrets
setup_registry_secrets() {
    log_info "Setting up container registry secrets..."
    
    # Create GitHub Container Registry token
    gh secret set CR_PAT --body "$(gh auth token)" --repo $REPO_OWNER/$REPO_NAME
    
    log_info "Container registry secrets set up."
}

# Setup Kubernetes secrets (optional)
setup_k8s_secrets() {
    log_info "Setting up Kubernetes secrets..."
    
    # Get kubeconfig content (base64 encoded)
    local kubeconfig=$(cat ~/.kube/config | base64)
    
    # Set kubeconfig as secret
    gh secret set KUBECONFIG --body "$kubeconfig" --repo $REPO_OWNER/$REPO_NAME
    
    log_info "Kubernetes secrets set up."
}

# Setup application secrets
setup_app_secrets() {
    log_info "Setting up application secrets..."
    
    # Add any application-specific secrets here
    # For example, API keys, database credentials, etc.
    
    # Example:
    # gh secret set API_KEY --body "your-api-key-here" --repo $REPO_OWNER/$REPO_NAME
    
    log_info "Application secrets set up."
}

# Setup environment-specific secrets
setup_environment_secrets() {
    local environment=${1:-"staging"}
    
    log_info "Setting up $environment environment secrets..."
    
    case $environment in
        "production")
            # Production-specific secrets
            gh secret set PROD_DOMAIN --body "your-production-domain.com" --repo $REPO_OWNER/$REPO_NAME
            gh secret set PROD_SSL_EMAIL --body "admin@your-production-domain.com" --repo $REPO_OWNER/$REPO_NAME
            ;;
        "staging")
            # Staging-specific secrets
            gh secret set STAGING_DOMAIN --body "staging.your-domain.com" --repo $REPO_OWNER/$REPO_NAME
            ;;
    esac
    
    log_info "$environment secrets set up."
}

# List all secrets
list_secrets() {
    log_info "Current secrets in repository:"
    gh secret list --repo $REPO_OWNER/$REPO_NAME
}

# Main function
main() {
    local environment=${1:-"staging"}
    
    log_info "Setting up GitHub secrets for $REPO_OWNER/$REPO_NAME"
    
    # Check prerequisites
    check_gh_cli
    
    # Setup different types of secrets
    setup_registry_secrets
    setup_k8s_secrets
    setup_app_secrets
    setup_environment_secrets $environment
    
    # List all secrets
    list_secrets
    
    log_info "GitHub secrets setup completed!"
    log_warn "Please review the secrets and ensure they are correct."
    log_info "You can now use the GitHub Actions workflow for automated deployment."
}

# Help function
show_help() {
    echo "Usage: $0 [REPO_OWNER] [REPO_NAME]"
    echo ""
    echo "REPO_OWNER: GitHub repository owner (default: yourusername)"
    echo "REPO_NAME: GitHub repository name (default: Sign-Language-To-Text-and-Speech-Conversion)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use default values"
    echo "  $0 myorg my-sign-language-app         # Use custom values"
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
