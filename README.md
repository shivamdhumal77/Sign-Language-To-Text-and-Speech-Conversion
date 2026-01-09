# Sign Language to Text and Speech Conversion

A professional real-time sign language recognition system that translates hand gestures into text using computer vision and deep learning. Built with Flask, OpenCV, and TensorFlow.

## 🚀 Features

- **Real-time Hand Gesture Recognition**: Advanced CNN-based sign language detection
- **Intelligent Text Processing**: Smart word completion and suggestion system
- **Professional Architecture**: Modular, scalable, and maintainable codebase
- **Containerized Deployment**: Docker support with production-ready configuration
- **Comprehensive Logging**: Structured logging with multiple levels
- **Environment Configuration**: Flexible configuration via environment variables
- **Health Monitoring**: Built-in health check endpoints
- **Error Handling**: Robust error handling and validation

## 📋 Prerequisites

- Python 3.8 or higher
- Webcam or camera device
- Git
- Docker and Docker Compose (for containerized deployment)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Sign-Language-To-Text-and-Speech-Conversion.git
   cd Sign-Language-To-Text-and-Speech-Conversion
   ```

2. **Create a virtual environment**
   ```bash
   # For Windows
   python -m venv venv
   .\venv\Scripts\activate

   # For macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Download the pre-trained model**
   - Ensure `sign_language_AZ_CNN.h5` is in the project root
   - The model should be automatically detected by the application

6. **Run the application**
   ```bash
   python run.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **For production with Nginx**
   ```bash
   docker-compose --profile production up --build
   ```

## 🏗️ Project Structure

```
Sign-Language-To-Text-and-Speech-Conversion/
├── src/                          # Source code
│   ├── config/                   # Configuration modules
│   │   ├── __init__.py
│   │   └── settings.py          # Application settings
│   ├── models/                   # ML models and dictionaries
│   │   ├── __init__.py
│   │   ├── sign_model.py        # Sign language recognition model
│   │   └── word_dictionary.py   # Word recommendations
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── hand_detector.py     # Hand detection service
│   │   └── video_processor.py   # Video processing service
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   └── logger.py            # Logging configuration
│   └── app.py                   # Flask application
├── docker/                       # Docker configuration
│   ├── app.Dockerfile           # Application Dockerfile
│   └── nginx.conf               # Nginx configuration
├── templates/                    # HTML templates
│   └── index.html               # Main web interface
├── logs/                         # Application logs
├── run.py                        # Main entry point
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Docker Compose configuration
├── .env.example                  # Environment variables template
├── sign_language_AZ_CNN.h5     # Pre-trained model
└── README.md                     # This file
```

## ⚙️ Configuration

The application can be configured using environment variables. Copy `.env.example` to `.env` and modify as needed:

### Key Configuration Options

- `MODEL_PATH`: Path to the trained model file
- `CAMERA_INDEX`: Camera device index (default: 0)
- `FLASK_HOST`: Flask server host (default: 0.0.0.0)
- `FLASK_PORT`: Flask server port (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `HAND_DETECTION_CONFIDENCE`: Hand detection confidence threshold
- `LETTER_COOLDOWN`: Time between letter additions
- `WORD_RECOMMENDATIONS_LIMIT`: Number of word suggestions

## 🌐 API Endpoints

### Core Endpoints

- `GET /`: Main application interface
- `GET /video_feed`: Live video stream with detection
- `GET /get_text`: Get current text state
- `POST /clear`: Clear current text
- `POST /append_suggestion`: Append suggested word
- `POST /delete_last`: Delete last character
- `POST /add_space`: Add space to text
- `GET /health`: Health check endpoint

### API Response Format

```json
{
  "sentence": "HELLO WORLD",
  "letter": "D",
  "recs": ["HELLO", "HELP", "HAPPY"]
}
```

## 🐳 Docker Configuration

### Development Docker

```bash
docker-compose up --build
```

### Production Docker with Nginx

```bash
docker-compose --profile production up --build
```

### Docker Volumes and Devices

- **Model Volume**: Read-only access to the ML model
- **Logs Volume**: Persistent log storage
- **Camera Device**: Direct access to webcam device
- **Templates Volume**: Read-only access to HTML templates

## 🔧 Development

### Code Structure

The application follows a modular architecture:

- **Configuration**: Centralized settings management
- **Models**: ML models and data structures
- **Services**: Business logic and processing
- **Utils**: Shared utilities and helpers
- **App**: Flask application and routing

### Adding New Features

1. Add configuration to `src/config/settings.py`
2. Implement business logic in `src/services/`
3. Add models or data structures in `src/models/`
4. Update the Flask app in `src/app.py`
5. Add tests and documentation

### Logging

The application uses structured logging with multiple levels:

```python
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

## 🔍 Troubleshooting

### Common Issues

1. **Camera not detected**
   - Check camera permissions
   - Verify camera index in configuration
   - Ensure no other applications are using the camera

2. **Model loading failed**
   - Verify model file exists and is readable
   - Check model path in configuration
   - Ensure TensorFlow dependencies are installed

3. **Docker camera access**
   - Grant device access: `--device /dev/video0:/dev/video0`
   - Check Docker daemon permissions
   - Verify camera device exists on host

4. **Performance issues**
   - Adjust prediction frequency
   - Optimize camera resolution
   - Check system resources

### Debug Mode

Enable debug mode for detailed error information:

```bash
export FLASK_DEBUG=True
python run.py
```

## 📊 Monitoring

### Health Checks

```bash
curl http://localhost:5000/health
```

### Logs

```bash
# View application logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f sign-language-app
```

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Configure production settings
   ```

2. **SSL Configuration**
   ```bash
   mkdir -p docker/ssl
   # Add SSL certificates
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose --profile production up -d
   ```

### Environment Variables

Production environment should include:

```bash
FLASK_DEBUG=False
LOG_LEVEL=WARNING
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Include docstrings for functions and classes
- Add comprehensive error handling
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/), [OpenCV](https://opencv.org/), and [TensorFlow](https://tensorflow.org/)
- Uses [cvzone](https://github.com/cvzone/cvzone) for hand tracking
- Inspired by the need for accessible communication tools

## 📞 Support

For questions, issues, or contributions:

- Open an issue on GitHub
- Check the troubleshooting section
- Review the API documentation
- Contact the maintainers

---

**Note**: This application requires a trained sign language model. Ensure the model file `sign_language_AZ_CNN.h5` is present before running the application.
