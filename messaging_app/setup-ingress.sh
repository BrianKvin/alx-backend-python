#!/bin/bash

# setup-ingress.sh - Automated Kubernetes Ingress Setup Script
# This script sets up Nginx Ingress Controller and configures Ingress for Django app

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# Configuration
APP_NAME="django-messaging-app"
SERVICE_NAME="django-messaging-service"
INGRESS_NAME="django-messaging-ingress"
NAMESPACE="default"

# Domain names
MAIN_DOMAIN="django-messaging.local"
API_DOMAIN="api.django-messaging.local"
DEV_DOMAIN="dev.django-messaging.local"
WWW_DOMAIN="www.django-messaging.local"

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if kubectl is available
    if ! command -v kubectl >/dev/null 2>&1; then
        print_error "kubectl is not installed. Please install it first."
        exit 1
    fi
    
    # Check if minikube is running
    if ! minikube status >/dev/null 2>&1; then
        print_error "Minikube is not running. Please start it first with: minikube start"
        exit 1
    fi
    
    # Check if the Django service exists
    if ! kubectl get service $SERVICE_NAME >/dev/null 2>&1; then
        print_error "Service '$SERVICE_NAME' not found. Please deploy the Django app first."
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Function to install Nginx Ingress Controller
install_ingress_controller() {
    print_header "=== INSTALLING NGINX INGRESS CONTROLLER ==="
    
    # Check if ingress addon is already enabled
    if minikube addons list | grep "ingress" | grep -q "enabled"; then
        print_success "Nginx Ingress Controller is already enabled"
    else
        print_status "Enabling Nginx Ingress Controller addon..."
        minikube addons enable ingress
        print_success "Nginx Ingress Controller enabled"
    fi
    
    # Wait for ingress controller to be ready
    print_status "Waiting for Ingress Controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    print_success "Nginx Ingress Controller is ready"
    
    # Show ingress controller status
    print_status "Ingress Controller pods:"
    kubectl get pods -n ingress-nginx
}

# Function to apply ingress configuration
apply_ingress_config() {
    print_header "=== APPLYING INGRESS CONFIGURATION ==="
    
    # Check if ingress.yaml exists
    if [[ ! -f "ingress.yaml" ]]; then
        print_error "ingress.yaml file not found in current directory"
        exit 1
    fi
    
    print_status "Applying Ingress configuration..."
    kubectl apply -f ingress.yaml
    
    print_success "Ingress configuration applied successfully"
    
    # Wait for ingress to be ready
    print_status "Waiting for Ingress to be ready..."
    sleep 10
    
    # Show ingress status
    print_status "Ingress resources:"
    kubectl get ingress
}

# Function to configure local DNS
configure_local_dns() {
    print_header "=== CONFIGURING LOCAL DNS ==="
    
    # Get minikube IP
    MINIKUBE_IP=$(minikube ip)
    print_status "Minikube IP: $MINIKUBE_IP"
    
    # Check if entries already exist in /etc/hosts
    if grep -q "$MAIN_DOMAIN" /etc/hosts; then
        print_warning "DNS entries already exist in /etc/hosts"
        print_status "Current entries:"
        grep -E "(django-messaging|api\.django-messaging)" /etc/hosts || true
    else
        print_status "Adding DNS entries to /etc/hosts..."
        
        # Create temporary hosts file
        cat << EOF > /tmp/django-hosts
# Django Messaging App - Kubernetes Ingress
$MINIKUBE_IP $MAIN_DOMAIN
$MINIKUBE_IP $API_DOMAIN
$MINIKUBE_IP $DEV_DOMAIN
$MINIKUBE_IP $WWW_DOMAIN
EOF
        
        print_status "The following entries will be added to /etc/hosts:"
        cat /tmp/django-hosts
        
        echo ""
        read -p "Do you want to add these entries to /etc/hosts? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo tee -a /etc/hosts < /tmp/django-hosts > /dev/null
            print_success "DNS entries added to /etc/hosts"
        else
            print_warning "DNS entries not added. You'll need to add them manually or use curl with Host header"
        fi
        
        rm -f /tmp/django-hosts
    fi
}

# Function to test ingress endpoints
test_ingress_endpoints() {
    print_header "=== TESTING INGRESS ENDPOINTS ==="
    
    MINIKUBE_IP=$(minikube ip)
    
    print_status "Testing Ingress endpoints..."
    
    # Test main domain
    echo ""
    print_status "Testing main domain ($MAIN_DOMAIN):"
    if curl -s -H "Host: $MAIN_DOMAIN" http://$MINIKUBE_IP/ >/dev/null 2>&1; then
        print_success "✅ Main domain is accessible"
    else
        print_warning "❌ Main domain test failed"
    fi
    
    # Test API domain
    print_status "Testing API domain ($API_DOMAIN):"
    if curl -s -H "Host: $API_DOMAIN" http://$MINIKUBE_IP/ >/dev/null 2>&1; then
        print_success "✅ API domain is accessible"
    else
        print_warning "❌ API domain test failed"
    fi
    
    # Test API path
    print_status "Testing API path (/api/):"
    if curl -s -H "Host: $MAIN_DOMAIN" http://$MINIKUBE_IP/api/ >/dev/null 2>&1; then
        print_success "✅ API path is accessible"
    else
        print_warning "❌ API path test failed"
    fi
    
    # Test admin path
    print_status "Testing admin path (/admin/):"
    if curl -s -H "Host: $MAIN_DOMAIN" http://$MINIKUBE_IP/admin/ >/dev/null 2>&1; then
        print_success "✅ Admin path is accessible"
    else
        print_warning "❌ Admin path test failed"
    fi
    
    # Test www redirect
    print_status "Testing www redirect:"
    if curl -s -I -H "Host: $WWW_DOMAIN" http://$MINIKUBE_IP/ | grep -q "301\|302"; then
        print_success "✅ WWW redirect is working"
    else
        print_warning "❌ WWW redirect test failed"
    fi
}

# Function to show ingress information
show_ingress_info() {
    print_header "=== INGRESS INFORMATION ==="
    
    MINIKUBE_IP=$(minikube ip)
    
    echo ""
    print_status "Ingress Controller Service:"
    kubectl get service -n ingress-nginx
    
    echo ""
    print_status "Ingress Resources:"
    kubectl get ingress
    
    echo ""
    print_status "Detailed Ingress Information:"
    kubectl describe ingress $INGRESS_NAME
    
    echo ""
    print_success "🎉 Ingress setup completed successfully!"
    echo ""
    print_status "Access your Django app at:"
    echo "  • Main site: http://$MAIN_DOMAIN/"
    echo "  • API only:  http://$API_DOMAIN/"
    echo "  • Admin:     http://$MAIN_DOMAIN/admin/"
    echo "  • API path:  http://$MAIN_DOMAIN/api/"
    echo "  • Dev site:  http://$DEV_DOMAIN/"
    echo ""
    
    print_status "Alternative access methods:"
    echo "  • Direct IP: http://$MINIKUBE_IP/ (with Host header)"
    echo "  • Tunnel:    minikube tunnel (then use http://localhost/)"
    echo ""
    
    print_status "Useful commands:"
    echo "  kubectl get ingress"
    echo "  kubectl describe ingress $INGRESS_NAME"
    echo "  kubectl logs -n ingress-nginx deployment/ingress-nginx-controller"
    echo "  minikube tunnel"
}

# Function to start minikube tunnel
start_tunnel() {
    print_header "=== STARTING MINIKUBE TUNNEL ==="
    
    print_status "Starting minikube tunnel for LoadBalancer access..."
    print_warning "This will require sudo privileges and will run in the background"
    print_status "After tunnel starts, you can access the app at http://localhost/"
    
    echo ""
    read -p "Do you want to start minikube tunnel? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Starting tunnel... (Press Ctrl+C to stop)"
        minikube tunnel
    else
        print_status "Tunnel not started. Use 'minikube tunnel' to start it manually."
    fi
}

# Function to monitor ingress
monitor_ingress() {
    print_header "=== MONITORING INGRESS ==="
    
    print_status "Starting ingress monitoring (Press Ctrl+C to stop)..."
    
    trap 'print_status "Stopping monitoring..."; exit 0' INT
    
    while true; do
        clear
        echo "=== INGRESS MONITORING ==="
        echo "Time: $(date)"
        echo ""
        
        echo "INGRESS RESOURCES:"
        kubectl get ingress
        echo ""
        
        echo "INGRESS CONTROLLER PODS:"
        kubectl get pods -n ingress-nginx
        echo ""
        
        echo "BACKEND SERVICE:"
        kubectl get service $SERVICE_NAME
        echo ""
        
        echo "BACKEND PODS:"
        kubectl get pods -l app=$APP_NAME
        echo ""
        
        echo "Press Ctrl+C to stop monitoring..."
        sleep 10
    done
}

# Main function
main() {
    echo "================================================"
    echo "    Kubernetes Ingress Setup Script"
    echo "        Django Messaging App"
    echo "================================================"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    echo ""
    
    # Install Nginx Ingress Controller
    install_ingress_controller
    echo ""
    
    # Apply Ingress configuration
    apply_ingress_config
    echo ""
    
    # Configure local DNS
    configure_local_dns
    echo ""
    
    # Test endpoints
    test_ingress_endpoints
    echo ""
    
    # Show information
    show_ingress_info
    echo ""
    
    # Ask about tunnel
    read -p "Do you want to start minikube tunnel for LoadBalancer access? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_tunnel
    fi
    
    # Ask about monitoring
    read -p "Do you want to start ingress monitoring? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        monitor_ingress
    fi
}

# Handle command line arguments
case "${1:-}" in
    "install")
        install_ingress_controller
        ;;
    "apply")
        apply_ingress_config
        ;;
    "test")
        test_ingress_endpoints
        ;;
    "tunnel")
        start_tunnel
        ;;
    "monitor")
        monitor_ingress
        ;;
    "info")
        show_ingress_info
        ;;
    *)
        main
        ;;
esac