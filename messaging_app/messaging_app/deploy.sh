#!/bin/bash

# deploy.sh - Django Messaging App Kubernetes Deployment Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration
APP_NAME="django-messaging-app"
IMAGE_NAME="django-messaging-app:latest"
NAMESPACE="default"

# Function to check if minikube is running
check_minikube() {
    print_status "Checking if minikube is running..."
    if ! minikube status >/dev/null 2>&1; then
        print_error "Minikube is not running. Please start it first with: minikube start"
        exit 1
    fi
    print_success "Minikube is running"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    
    # Check if Dockerfile exists
    if [[ ! -f "Dockerfile" ]]; then
        print_error "Dockerfile not found in current directory"
        print_status "Please ensure you're running this script from the messaging_app directory"
        exit 1
    fi
    
    # Use minikube's Docker daemon
    eval $(minikube docker-env)
    
    # Build the Docker image
    docker build -t $IMAGE_NAME .
    
    print_success "Docker image built successfully"
}

# Function to generate secret key
generate_secret() {
    print_status "Generating Django secret key..."
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    SECRET_KEY_B64=$(echo -n "$SECRET_KEY" | base64)
    
    # Update the secret in deployment.yaml
    sed -i.bak "s/secret-key: .*/secret-key: $SECRET_KEY_B64/" deployment.yaml
    
    print_success "Secret key generated and updated"
}

# Function to apply Kubernetes manifests
apply_manifests() {
    print_status "Applying Kubernetes manifests..."
    
    # Apply the deployment
    kubectl apply -f deployment.yaml
    
    print_success "Kubernetes manifests applied successfully"
}

# Function to wait for deployment
wait_for_deployment() {
    print_status "Waiting for deployment to be ready..."
    
    # Wait for the deployment to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/$APP_NAME
    
    print_success "Deployment is ready!"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    echo ""
    echo "=== PODS ==="
    kubectl get pods -l app=$APP_NAME
    
    echo ""
    echo "=== SERVICES ==="
    kubectl get services -l app=$APP_NAME
    
    echo ""
    echo "=== DEPLOYMENT STATUS ==="
    kubectl get deployment $APP_NAME
    
    echo ""
    echo "=== RECENT POD LOGS ==="
    POD_NAME=$(kubectl get pods -l app=$APP_NAME -o jsonpath='{.items[0].metadata.name}')
    if [[ -n "$POD_NAME" ]]; then
        print_status "Showing logs for pod: $POD_NAME"
        kubectl logs $POD_NAME --tail=20
    fi
}

# Function to get service URL
get_service_url() {
    print_status "Getting service access information..."
    
    SERVICE_NAME="django-messaging-service"
    
    echo ""
    print_success "Your Django app is deployed and running!"
    echo ""
    echo "To access your application:"
    echo "1. Port forward to access the service:"
    echo "   kubectl port-forward service/$SERVICE_NAME 8080:80"
    echo "   Then access: http://localhost:8080"
    echo ""
    echo "2. Or use minikube service:"
    echo "   minikube service $SERVICE_NAME"
    echo ""
    
    print_status "Useful commands for monitoring:"
    echo "  kubectl get pods -l app=$APP_NAME"
    echo "  kubectl logs <pod-name>"
    echo "  kubectl describe pod <pod-name>"
    echo "  kubectl exec -it <pod-name> -- /bin/bash"
}

# Function to show logs from all pods
show_all_logs() {
    print_status "Fetching logs from all pods..."
    
    PODS=$(kubectl get pods -l app=$APP_NAME -o jsonpath='{.items[*].metadata.name}')
    
    for pod in $PODS; do
        echo ""
        echo "=== LOGS FROM POD: $pod ==="
        kubectl logs $pod --tail=50
        echo "=================================="
    done
}

# Main deployment function
main() {
    echo "================================================"
    echo "   Django Messaging App Kubernetes Deployment"
    echo "================================================"
    echo ""
    
    # Check if minikube is running
    check_minikube
    echo ""
    
    # Build Docker image
    build_image
    echo ""
    
    # Generate secret key
    generate_secret
    echo ""
    
    # Apply Kubernetes manifests
    apply_manifests
    echo ""
    
    # Wait for deployment to be ready
    wait_for_deployment
    echo ""
    
    # Verify deployment
    verify_deployment
    echo ""
    
    # Show how to access the service
    get_service_url
    echo ""
    
    # Ask if user wants to see all logs
    read -p "Do you want to see detailed logs from all pods? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_all_logs
    fi
}

# Handle command line arguments
case "${1:-}" in
    "logs")
        show_all_logs
        ;;
    "status")
        verify_deployment
        ;;
    "url")
        get_service_url
        ;;
    *)
        main
        ;;
esac