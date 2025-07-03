"""
Canvas RAG v2 - Multimodal Architecture Drawing Query System

A comprehensive RAG system for querying Canvas LMS content with multimodal capabilities.
"""

__version__ = "2.0.0"
__author__ = "Canvas RAG Team"

from .config.settings import Settings
from .utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

logger.info(f"Canvas RAG v{__version__} initialized")
