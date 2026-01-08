# Sign Language to Text and Speech Conversion

A real-time sign language recognition system that translates hand gestures into text and speech using computer vision and deep learning.

## Features

- Real-time hand gesture recognition
- Text output of recognized signs
- Speech synthesis for text output
- Voice command integration
- History of transcriptions
- Suggestion system for word completion
- Responsive web interface

## Prerequisites

- Python 3.8 or higher
- Webcam
- Internet connection (for first-time setup)
- Windows/macOS/Linux

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Sign-Language-To-Text-and-Speech-Conversion.git
   cd Sign-Language-To-Text-and-Speech-Conversion
   ```

2. **Create a virtual environment (recommended)**
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

4. **Download the pre-trained model**
   - The model file `sign_language_AZ_CNN.h5` should be in the project root
   - If not, download it from the provided link in the project repository

## Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Access the application**
   - Open a web browser and navigate to:
     ```
     http://localhost:5000
     ```

3. **Using the application**
   - Allow camera access when prompted
   - Position your hand in the camera view to see real-time sign language recognition
   - Use the interface to control voice input/output and view transcriptions

## Project Structure

```
Sign-Language-To-Text-and-Speech-Conversion/
├── app.py                # Main application file
├── requirements.txt      # Python dependencies
├── sign_language_AZ_CNN.h5  # Pre-trained model
├── templates/
│   └── index.html        # Web interface
└── README.md             # This file
```

## Usage Guide

### Sign Language Recognition
1. Ensure good lighting in your environment
2. Position your hand within the camera frame
3. Perform sign language gestures clearly
4. The system will display recognized letters and words in real-time

### Voice Commands
- Click the microphone button to start voice input
- Speak clearly into your microphone
- Click stop to end voice input
- The transcribed text will appear in the history

### Controls
- **Speak**: Convert text to speech
- **Clear**: Clear the current text
- **Start/Stop Recording**: Control voice input
- **History**: View previous transcriptions
- **Suggestions**: Click on suggested words to complete your sentence

## Troubleshooting

### Common Issues
1. **Webcam not detected**
   - Ensure no other application is using the webcam
   - Check if the webcam is properly connected

2. **Dependency installation fails**
   - Make sure you have the latest version of pip:
     ```bash
     pip install --upgrade pip
     ```
   - Try installing dependencies one by one if the complete installation fails

3. **Model not found**
   - Ensure `sign_language_AZ_CNN.h5` is in the project root
   - Check the file permissions

## Performance Tips

- Use the application in a well-lit environment
- Keep your hand within the camera frame
- Ensure your webcam has at least 720p resolution for better accuracy
- Close other applications using the webcam for better performance

## Docker Setup (Alternative)

For containerized deployment, see [README-Docker.md](README-Docker.md) for detailed Docker instructions.

### Quick Docker Commands

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t sign-language-app .
docker run -p 5000:5000 sign-language-app
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Flask, OpenCV, and TensorFlow
- Uses the cvzone library for hand tracking
- Inspired by the need for accessible communication tools

## Contact

For any questions or feedback, please contact [Your Email] or open an issue on GitHub.
