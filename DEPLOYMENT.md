# Deployment Guide

This guide provides comprehensive instructions for deploying the Sign Language Recognition application to various environments.

## 🚀 Quick Start

### Local Development

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start local development
./scripts/local-deploy.sh start
```

### Production Deployment

```bash
# Set up GitHub secrets
./scripts/setup-github-secrets.sh

# Deploy to production
./scripts/deploy.sh production main
```

## 📋 Deployment Options

### 1. Local Development

Run the application locally using Docker:

```bash
# Start the application
./scripts/local-deploy.sh start

# View logs
./scripts/local-deploy.sh logs

# Stop the application
./scripts/local-deploy.sh stop
```

### 2. Docker Compose

For simple containerized deployment:

```bash
# Development
docker-compose up --build

# Production with Nginx
docker-compose --profile production up --build -d
```

### 3. Kubernetes Production

For scalable production deployment:

```bash
# Deploy to staging
./scripts/deploy.sh staging develop

# Deploy to production
./scripts/deploy.sh production main
```

### 4. GitHub Actions CI/CD

Automated deployment via GitHub Actions:

- **Push to `develop`**: Automatic staging deployment
- **Push to `main`**: Automatic production deployment
- **Pull Requests**: Automated testing and validation

## 🔧 Prerequisites

### For Local Development

- Docker and Docker Compose
- Python 3.8+ (for development)
- Webcam device (for testing)

### For Kubernetes Deployment

- Kubernetes cluster (v1.20+)
- kubectl configured
- Container registry access
- Ingress controller (nginx)

### For GitHub Actions

- GitHub repository
- GitHub CLI (for secret setup)
- Container registry permissions

## 🐳 Docker Configuration

### Build Image

```bash
# Build locally
docker build -f ./docker/app.Dockerfile -t sign-language-app .

# Tag for registry
docker tag sign-language-app ghcr.io/yourusername/sign-language-to-text-and-speech-conversion:latest

# Push to registry
docker push ghcr.io/yourusername/sign-language-to-text-and-speech-conversion:latest
```

### Environment Variables

Key environment variables for deployment:

```bash
# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# Logging
LOG_LEVEL=INFO

# Camera Settings
CAMERA_INDEX=0
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# Model Settings
MODEL_PATH=/app/sign_language_AZ_CNN.h5
```

## ☸️ Kubernetes Deployment

### Namespace Setup

```bash
# Create namespace
kubectl apply -f k8s/namespace.yml
```

### Configuration

```bash
# Apply ConfigMaps
kubectl apply -f k8s/configmap.yml -n sign-language-app
```

### Deployment

```bash
# Deploy application
kubectl apply -f k8s/deployment.yml -n sign-language-app

# Expose service
kubectl apply -f k8s/service.yml -n sign-language-app

# Setup autoscaling
kubectl apply -f k8s/hpa.yml -n sign-language-app
```

### Ingress (Production)

```bash
# Setup ingress with SSL
kubectl apply -f k8s/ingress.yml -n sign-language-app
```

### Monitoring

```bash
# Check deployment status
kubectl get pods -n sign-language-app

# View logs
kubectl logs -f deployment/sign-language-app -n sign-language-app

# Check HPA status
kubectl get hpa -n sign-language-app
```

## 🔐 Security Configuration

### Secrets Management

#### GitHub Secrets

```bash
# Setup all required secrets
./scripts/setup-github-secrets.sh

# List current secrets
gh secret list --repo yourusername/Sign-Language-To-Text-and-Speech-Conversion
```

#### Kubernetes Secrets

```bash
# Create secret for model file
kubectl create secret generic sign-language-model \
  --from-file=sign_language_AZ_CNN.h5 \
  -n sign-language-app

# Create secret for environment variables
kubectl create secret generic sign-language-secrets \
  --from-env-file=.env \
  -n sign-language-app
```

### SSL/TLS Configuration

#### Let's Encrypt with Cert-Manager

```yaml
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# ClusterIssuer for Let's Encrypt
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@your-domain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

## 📊 Monitoring and Logging

### Application Logs

```bash
# Local logs
tail -f logs/app.log

# Docker logs
docker logs -f sign-language-app

# Kubernetes logs
kubectl logs -f deployment/sign-language-app -n sign-language-app
```

### Health Checks

```bash
# Local health check
curl http://localhost:5000/health

# Kubernetes health check
kubectl port-forward service/sign-language-app-service 5000:80 -n sign-language-app
curl http://localhost:5000/health
```

### Metrics Collection

Consider adding Prometheus and Grafana for monitoring:

```yaml
# Prometheus ServiceMonitor
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: sign-language-app
  namespace: sign-language-app
spec:
  selector:
    matchLabels:
      app: sign-language-app
  endpoints:
  - port: http
    path: /metrics
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The deployment pipeline includes:

1. **Testing**: Multi-Python version testing, linting, coverage
2. **Building**: Docker image building and pushing
3. **Deployment**: Automated deployment to staging/production
4. **Validation**: Post-deployment health checks

### Branch Strategy

- **`main`**: Production branch
- **`develop`**: Staging branch
- **`feature/*`**: Feature branches (testing only)

### Environment Promotion

```bash
# Promote staging to production
git checkout main
git merge develop
git push origin main
```

## 🚨 Troubleshooting

### Common Issues

#### Camera Access in Docker

```bash
# Grant camera access to container
docker run --device /dev/video0:/dev/video0 sign-language-app

# For multiple cameras
docker run --device /dev/video0:/dev/video0 --device /dev/video1:/dev/video1 sign-language-app
```

#### Model Loading Issues

```bash
# Check model file permissions
ls -la sign_language_AZ_CNN.h5

# Verify model in container
docker exec -it sign-language-app ls -la /app/sign_language_AZ_CNN.h5
```

#### Memory Issues

```bash
# Check resource usage
kubectl top pods -n sign-language-app

# Adjust resource limits
kubectl edit deployment sign-language-app -n sign-language-app
```

#### SSL Certificate Issues

```bash
# Check certificate status
kubectl describe certificate sign-language-app-tls -n sign-language-app

# Debug cert-manager
kubectl logs -f deployment/cert-manager -n cert-manager
```

### Debug Commands

```bash
# Port forwarding for local debugging
kubectl port-forward service/sign-language-app-service 5000:80 -n sign-language-app

# Exec into container
kubectl exec -it deployment/sign-language-app -n sign-language-app -- /bin/bash

# Describe resources
kubectl describe pod -l app=sign-language-app -n sign-language-app
kubectl describe service sign-language-app-service -n sign-language-app
```

## 📈 Performance Optimization

### Horizontal Scaling

```bash
# Manual scaling
kubectl scale deployment sign-language-app --replicas=5 -n sign-language-app

# Check HPA status
kubectl get hpa -n sign-language-app
```

### Resource Tuning

Adjust resource requests and limits in `k8s/deployment.yml`:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Caching

Consider adding Redis for session caching:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    spec:
      containers:
      - name: redis
        image: redis:alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

## 🔧 Maintenance

### Updates

```bash
# Update application
./scripts/deploy.sh production v1.1.0

# Rollback deployment
kubectl rollout undo deployment/sign-language-app -n sign-language-app
```

### Backup

```bash
# Backup configuration
kubectl get all -n sign-language-app -o yaml > backup.yaml

# Backup secrets
kubectl get secrets -n sign-language-app -o yaml > secrets-backup.yaml
```

### Cleanup

```bash
# Remove all resources
kubectl delete namespace sign-language-app

# Clean up Docker
docker system prune -a
```

## 📞 Support

For deployment issues:

1. Check the troubleshooting section
2. Review application logs
3. Verify configuration files
4. Check GitHub Actions workflow logs
5. Open an issue on GitHub

---

**Note**: Ensure you have proper permissions and access rights for all deployment targets before proceeding.
