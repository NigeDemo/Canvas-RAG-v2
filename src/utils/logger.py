"""Logging configuration for Canvas RAG system."""

import logging
import sys
from pathlib import Path
from typing import Optional
from loguru import logger as loguru_logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    if name is None:
        name = "canvas_rag"
        
    # Configure loguru logger
    loguru_logger.remove()  # Remove default handler
    
    # Add console handler
    loguru_logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}",
        level="INFO"
    )
    
    # Add file handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    loguru_logger.add(
        log_dir / "canvas_rag.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days"
    )
    
    # Create standard logger that forwards to loguru
    class LoguruHandler(logging.Handler):
        def emit(self, record):
            try:
                level = loguru_logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
                
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
                
            loguru_logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    std_logger = logging.getLogger(name)
    std_logger.handlers = [LoguruHandler()]
    std_logger.setLevel(logging.DEBUG)
    
    return std_logger
