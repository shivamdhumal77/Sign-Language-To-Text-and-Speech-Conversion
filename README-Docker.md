# Docker Setup for Sign Language to Text and Speech Conversion

This guide explains how to run the Sign Language to Text and Speech Conversion application using Docker.

## Prerequisites

- Docker Desktop installed on your system
- Docker Compose (usually included with Docker Desktop)
- For Linux: Webcam access permissions

## Quick Start

### Option 1: Using Docker Compose (Recommended)

#### Linux/macOS:
```bash
# Build and run the container
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

#### Windows:
```bash
# Use the Windows-specific compose file
docker-compose -f docker-compose-windows.yml up --build

# Or run in detached mode
docker-compose -f docker-compose-windows.yml up --build -d
```

### Option 2: Using Docker directly

```bash
# Build the image
docker build -t sign-language-app .

# Run the container
docker run -p 5000:5000 -v $(pwd)/sign_language_AZ_CNN.h5:/app/sign_language_AZ_CNN.h5:ro sign-language-app
```

## Accessing the Application

After starting the container, open your web browser and navigate to:
```
http://localhost:5000
```

## Webcam Access Setup

### Linux
The docker-compose.yml file includes webcam device mapping. If you encounter permission issues:

```bash
# Add your user to the video group
sudo usermod -a -G video $USER

# Then logout and login again, or restart your session
```

### Windows
Webcam access in Docker on Windows requires additional setup:

1. **Enable Docker Desktop's WSL 2 integration**
2. **Install a virtual camera driver** (optional, for better compatibility)
3. **Use Windows-specific compose file**:
   ```bash
   docker-compose -f docker-compose-windows.yml up --build
   ```

### macOS
For macOS, you may need to:
1. Grant Docker Desktop camera permissions in System Preferences
2. Use the standard docker-compose.yml file

## Docker Commands

### Building the Image
```bash
docker build -t sign-language-app .
```

### Running the Container
```bash
# Interactive mode
docker run -it -p 5000:5000 sign-language-app

# Detached mode
docker run -d -p 5000:5000 --name sign-language-converter sign-language-app
```

### Managing Containers
```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Stop a container
docker stop sign-language-converter

# Remove a container
docker rm sign-language-converter

# View logs
docker logs sign-language-converter

# Follow logs in real-time
docker logs -f sign-language-converter
```

### Managing Images
```bash
# List images
docker images

# Remove an image
docker rmi sign-language-app

# Remove all unused images
docker image prune
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 5000
   netstat -tulpn | grep :5000
   
   # Or use a different port
   docker run -p 5001:5000 sign-language-app
   ```

2. **Webcam not accessible**
   - Ensure Docker has camera permissions
   - On Linux: Check `/dev/video0` exists and permissions
   - On Windows: Use docker-compose-windows.yml

3. **Memory issues**
   ```bash
   # Increase Docker memory allocation in Docker Desktop settings
   # Or run with more memory:
   docker run --memory=4g -p 5000:5000 sign-language-app
   ```

4. **Build fails**
   ```bash
   # Clean build
   docker system prune -f
   docker build --no-cache -t sign-language-app .
   ```

### Debugging

To debug issues, run the container in interactive mode:

```bash
docker run -it -p 5000:5000 sign-language-app /bin/bash
```

Then you can:
- Check Python installation: `python --version`
- Test OpenCV: `python -c "import cv2; print(cv2.__version__)"`
- Check TensorFlow: `python -c "import tensorflow as tf; print(tf.__version__)"`

## Production Considerations

For production deployment, consider:

1. **Security**: Remove debug mode from Flask
2. **Performance**: Use multi-stage builds
3. **Monitoring**: Add health checks
4. **Scaling**: Use orchestration tools like Kubernetes

## Environment Variables

You can customize the application using environment variables:

```bash
docker run -e FLASK_ENV=production -p 5000:5000 sign-language-app
```

Available variables:
- `FLASK_ENV`: Set to 'production' for production mode
- `PYTHONUNBUFFERED`: Set to '1' for immediate log output
- `PYTHONDONTWRITEBYTECODE`: Set to '1' to prevent .pyc files

## Volumes

The application uses volumes for:
- Model file: `./sign_language_AZ_CNN.h5:/app/sign_language_AZ_CNN.h5:ro`
- Templates: `./templates:/app/templates:ro`

The `:ro` flag makes them read-only for security.

## Support

If you encounter issues with Docker setup:
1. Check Docker Desktop is running
2. Verify all files are present in the project directory
3. Check system logs for Docker-related errors
4. Ensure your system meets the minimum requirements
