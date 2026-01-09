#!/usr/bin/env python3
"""
Sign Language to Text and Speech Conversion - Main Entry Point

This is the main entry point for the application. It initializes and starts
the Flask web server with all necessary services.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.app import app, initialize_services, cleanup, logger
from src.config.settings import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

def main():
    """Main entry point for the application."""
    try:
        logger.info("Starting Sign Language Recognition Application...")
        
        # Initialize all services
        initialize_services()
        
        # Setup cleanup on exit
        import atexit
        atexit.register(cleanup)
        
        logger.info(f"Starting Flask server on {FLASK_HOST}:{FLASK_PORT}")
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG,
            threaded=True
        )
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)
    
    finally:
        cleanup()

if __name__ == "__main__":
    main()
