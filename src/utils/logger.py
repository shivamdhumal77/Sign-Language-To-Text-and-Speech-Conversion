import logging
import sys
from pathlib import Path

def setup_logger(name: str = "sign_language_app", level: str = "INFO", 
                log_format: str = None) -> logging.Logger:
    """Setup logger with console and file handlers."""
    
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional - creates logs directory)
    try:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(logs_dir / "app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)
