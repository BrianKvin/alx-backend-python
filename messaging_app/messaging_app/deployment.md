Deployment Instructions:
Step 1: Prepare Your Environment
bash# Make sure you're in the messaging_app directory
cd alx-backend-python/messaging_app

# Ensure minikube is running
minikube start
Step 2: Create Requirements File
Create a requirements.txt file with your Django dependencies:
Django>=4.2.0
djangorestframework
django-cors-headers
gunicorn
psycopg2-binary
Step 3: Deploy Using the Script
bash# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
Step 4: Manual Deployment (Alternative)
If you prefer manual deployment:
bash# Build Docker image (using minikube's Docker daemon)
eval $(minikube docker-env)
docker build -t django-messaging-app:latest .

# Apply Kubernetes manifests
kubectl apply -f deployment.yaml

# Verify deployment
kubectl get pods
kubectl get services
🔍 Verification Commands:
bash# Check pods
kubectl get pods

# Check logs of a specific pod
kubectl logs <pod-name>

# Check all pods with app label
kubectl get pods -l app=django-messaging-app

# Check service
kubectl get services

# Port forward to access the app
kubectl port-forward service/django-messaging-service 8080:80
📋 Key Features of the Deployment:

High Availability: 3 replicas for redundancy
Health Checks: Liveness and readiness probes
Resource Management: CPU and memory limits/requests
Security: Non-root user, secrets management
Storage: Persistent volumes for static and media files
Internal Access: ClusterIP service keeps it internal

🛠 Troubleshooting:
If you encounter issues:
bash# Check deployment status
./deploy.sh status

# View detailed logs
./deploy.sh logs

# Check pod details
kubectl describe pod <pod-name>