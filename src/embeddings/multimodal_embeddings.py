"""Multimodal embedding models for Canvas RAG system."""

import base64
from typing import List, Dict, Any, Union, Optional
import numpy as np
from abc import ABC, abstractmethod

try:
    import torch
    from sentence_transformers import SentenceTransformer
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingModel(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def embed_text(self, texts: List[str]) -> np.ndarray:
        """Embed text content."""
        pass
    
    @abstractmethod
    def embed_multimodal(self, content: List[Dict[str, Any]]) -> np.ndarray:
        """Embed multimodal content (text + images)."""
        pass

class NomicEmbedModel(EmbeddingModel):
    """Nomic Embed Multimodal model wrapper."""
    
    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1.5"):
        """
        Initialize Nomic embedding model.
        
        Args:
            model_name: Name of the Nomic model to use
        """
        if not TORCH_AVAILABLE:
            raise ImportError("torch and sentence-transformers are required for Nomic embeddings")
        
        self.model_name = model_name
        try:
            # For now, use sentence-transformers as a placeholder
            # In production, this would use the actual Nomic API or model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, texts: List[str]) -> np.ndarray:
        """
        Embed text content using Nomic model.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Numpy array of embeddings
        """
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding texts: {e}")
            return np.array([])
    
    def embed_multimodal(self, content: List[Dict[str, Any]]) -> np.ndarray:
        """
        Embed multimodal content (text + images).
        
        Args:
            content: List of content dictionaries with text and/or images
            
        Returns:
            Numpy array of embeddings
        """
        try:
            # For multimodal content, we'll combine text and image descriptions
            combined_texts = []
            
            for item in content:
                text_parts = []
                
                # Add text content
                if "text" in item and item["text"]:
                    text_parts.append(item["text"])
                
                # Add image metadata as text for now
                # TODO: Replace with actual multimodal embedding when Nomic multimodal is available
                if "image_base64" in item:
                    text_parts.append(f"[IMAGE: {item.get('filename', 'image')}]")
                    
                    # Add any alt text or descriptions
                    if "alt_text" in item and item["alt_text"]:
                        text_parts.append(f"Alt text: {item['alt_text']}")
                
                # Add metadata
                if "title" in item and item["title"]:
                    text_parts.append(f"Title: {item['title']}")
                
                if "page_number" in item:
                    text_parts.append(f"Page {item['page_number']}")
                
                combined_text = " ".join(text_parts) if text_parts else "[EMPTY_CONTENT]"
                combined_texts.append(combined_text)
            
            return self.embed_text(combined_texts)
            
        except Exception as e:
            logger.error(f"Error embedding multimodal content: {e}")
            return np.array([])

class OpenAIEmbedModel(EmbeddingModel):
    """OpenAI embedding model wrapper."""
    
    def __init__(self, model_name: str = "text-embedding-3-large"):
        """
        Initialize OpenAI embedding model.
        
        Args:
            model_name: Name of OpenAI embedding model
        """
        try:
            import openai
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            self.model_name = model_name
            logger.info(f"Initialized OpenAI embedding model: {model_name}")
        except ImportError:
            raise ImportError("openai package is required for OpenAI embeddings")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    def embed_text(self, texts: List[str]) -> np.ndarray:
        """
        Embed text using OpenAI API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Numpy array of embeddings
        """
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            return np.array(embeddings)
            
        except Exception as e:
            logger.error(f"Error getting OpenAI embeddings: {e}")
            return np.array([])
    
    def embed_multimodal(self, content: List[Dict[str, Any]]) -> np.ndarray:
        """
        Embed multimodal content using text embeddings.
        
        Args:
            content: List of content dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        # Convert multimodal content to text descriptions
        texts = []
        for item in content:
            text_parts = []
            
            if "text" in item and item["text"]:
                text_parts.append(item["text"])
            
            if "image_base64" in item:
                text_parts.append(f"[Image content from {item.get('filename', 'file')}]")
                if "alt_text" in item and item["alt_text"]:
                    text_parts.append(f"Description: {item['alt_text']}")
            
            combined_text = " ".join(text_parts) if text_parts else "[Empty content]"
            texts.append(combined_text)
        
        return self.embed_text(texts)

class EmbeddingManager:
    """Manages embedding models and provides unified interface."""
    
    def __init__(self, model_type: str = "nomic", **kwargs):
        """
        Initialize embedding manager.
        
        Args:
            model_type: Type of embedding model ("nomic", "openai")
            **kwargs: Additional arguments for model initialization
        """
        self.model_type = model_type
        
        if model_type == "nomic":
            self.model = NomicEmbedModel(**kwargs)
        elif model_type == "openai":
            self.model = OpenAIEmbedModel(**kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        logger.info(f"Initialized embedding manager with {model_type} model")
    
    def embed_content(self, content: List[Dict[str, Any]]) -> np.ndarray:
        """
        Embed content using the configured model.
        
        Args:
            content: List of content dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        return self.model.embed_multimodal(content)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string.
        
        Args:
            query: Query string to embed
            
        Returns:
            Numpy array with single embedding
        """
        return self.model.embed_text([query])[0]
