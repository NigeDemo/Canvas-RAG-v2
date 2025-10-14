"""Vision processor for coordinating image analysis tasks."""

import hashlib
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
import pickle

from PIL import Image
import requests
from io import BytesIO

from .vision_providers import get_vision_provider, VisionProvider
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

class VisionCache:
    """Simple file-based cache for vision analysis results."""
    
    def __init__(self, cache_dir: str = None, ttl_hours: int = 24):
        """
        Initialize vision cache.
        
        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time-to-live in hours
        """
        self.cache_dir = Path(cache_dir or settings.cache_dir or "cache/vision")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        
        logger.info(f"Initialized vision cache at {self.cache_dir}")
    
    def _get_cache_key(self, image_data: Union[str, bytes], prompt: str, provider: str) -> str:
        """Generate cache key for image analysis."""
        if isinstance(image_data, str):
            data_hash = hashlib.md5(image_data.encode()).hexdigest()
        else:
            data_hash = hashlib.md5(image_data).hexdigest()
        
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        return f"{provider}_{data_hash}_{prompt_hash}"
    
    def get(self, image_data: Union[str, bytes], prompt: str, provider: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result."""
        try:
            cache_key = self._get_cache_key(image_data, prompt, provider)
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            if not cache_file.exists():
                return None
            
            # Check if cache is still valid
            if datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime) > self.ttl:
                cache_file.unlink()
                return None
            
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def set(self, image_data: Union[str, bytes], prompt: str, provider: str, result: Dict[str, Any]):
        """Cache analysis result."""
        try:
            cache_key = self._get_cache_key(image_data, prompt, provider)
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
                
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")

class VisionProcessor:
    """Main vision processing coordinator."""
    
    def __init__(self, 
                 primary_provider: str = "openai",
                 fallback_provider: str = "claude",
                 use_cache: bool = True,
                 cache_ttl_hours: int = 24):
        """
        Initialize vision processor.
        
        Args:
            primary_provider: Primary vision provider
            fallback_provider: Fallback vision provider
            use_cache: Whether to use caching
            cache_ttl_hours: Cache time-to-live in hours
        """
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        self.use_cache = use_cache
        
        # Initialize providers
        self.providers = {}
        try:
            self.providers[primary_provider] = get_vision_provider(primary_provider)
        except Exception as e:
            logger.warning(f"Failed to initialize primary provider {primary_provider}: {e}")
        
        try:
            if fallback_provider and fallback_provider != primary_provider:
                self.providers[fallback_provider] = get_vision_provider(fallback_provider)
        except Exception as e:
            logger.warning(f"Failed to initialize fallback provider {fallback_provider}: {e}")
        
        if not self.providers:
            raise RuntimeError("No vision providers available")
        
        # Initialize cache
        self.cache = VisionCache(ttl_hours=cache_ttl_hours) if use_cache else None
        
        logger.info(f"Initialized VisionProcessor with providers: {list(self.providers.keys())}")
    
    def _get_provider(self, provider_name: str = None) -> VisionProvider:
        """Get vision provider instance."""
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name]
        
        # Use primary provider
        if self.primary_provider in self.providers:
            return self.providers[self.primary_provider]
        
        # Use any available provider
        return next(iter(self.providers.values()))
    
    def _download_image(self, url: str) -> bytes:
        """Download image from URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            raise
    
    def _detect_image_format(self, image_data: bytes) -> str:
        """Detect image format from bytes."""
        if image_data.startswith(b'\xff\xd8\xff'):
            return 'jpeg'
        elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png'
        elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
            return 'gif'
        elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
            return 'webp'
        elif image_data.startswith(b'BM'):
            return 'bmp'
        else:
            return 'unknown'
    
    def _convert_to_supported_format(self, image_data: bytes, current_format: str) -> bytes:
        """Convert image to supported format if needed.
        
        Converts BMP and other unsupported formats to PNG for Vision API compatibility.
        
        Args:
            image_data: Raw image bytes
            current_format: Detected image format
            
        Returns:
            Converted image data as PNG bytes
            
        Raises:
            ValueError: If the image cannot be read or converted
        """
        # Supported formats for Vision APIs
        supported_formats = ['png', 'jpeg', 'gif', 'webp']
        
        if current_format in supported_formats:
            return image_data
        
        # Convert unsupported formats (BMP, etc.) to PNG
        try:
            logger.info(f"Converting {current_format.upper()} to PNG for Vision API compatibility")
            
            # Open the image - this will fail if not a valid image file
            img = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary (for RGBA, P, etc.)
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Save as PNG
            output = BytesIO()
            img.save(output, format='PNG')
            converted_data = output.getvalue()
            
            logger.info(f"Successfully converted {current_format.upper()} to PNG ({len(image_data)} -> {len(converted_data)} bytes)")
            return converted_data
            
        except Exception as e:
            # PIL cannot read this file - it's not a valid image
            logger.warning(f"Cannot convert {current_format} to PNG: {e}. File is not a valid image, skipping.")
            raise ValueError(f"Invalid or unsupported image file: {e}")
    
    def _prepare_image_data(self, image_input: Union[str, bytes, Path]) -> bytes:
        """Prepare image data from various input types.
        
        This method:
        1. Loads image from URL, file path, or bytes
        2. Validates the image data
        3. Detects the image format
        4. Converts unsupported formats (like BMP) to PNG
        
        Format conversion happens HERE (before caching) to ensure cache
        only stores compatible formats.
        """
        image_data = None
        
        if isinstance(image_input, bytes):
            image_data = image_input
        elif isinstance(image_input, str):
            if image_input.startswith(('http://', 'https://')):
                image_data = self._download_image(image_input)
            else:
                # Assume it's a file path
                image_data = Path(image_input).read_bytes()
        elif isinstance(image_input, Path):
            image_data = image_input.read_bytes()
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
        
        # Validate image data
        if not image_data:
            raise ValueError("Empty image data")
        
        if len(image_data) < 10:
            raise ValueError("Image data too small to be valid")
        
        # Detect format and convert if needed (BEFORE caching)
        image_format = self._detect_image_format(image_data)
        
        # Convert unsupported or unknown formats to PNG
        if image_format in ['png', 'jpeg', 'gif', 'webp']:
            # Already in supported format, no conversion needed
            pass
        elif image_format == 'unknown':
            logger.warning(f"Unknown image format detected, attempting conversion via PIL")
            image_data = self._convert_to_supported_format(image_data, image_format)
        else:
            # Known unsupported format (BMP, etc.)
            logger.info(f"{image_format.upper()} format detected, converting to PNG")
            image_data = self._convert_to_supported_format(image_data, image_format)
        
        return image_data
    
    def analyze_image(self, 
                     image_input: Union[str, bytes, Path],
                     prompt: str,
                     provider: str = None,
                     use_fallback: bool = True,
                     **kwargs) -> Dict[str, Any]:
        """
        Analyze image with vision AI.
        
        Args:
            image_input: Image data (URL, file path, or bytes)
            prompt: Analysis prompt
            provider: Specific provider to use
            use_fallback: Whether to use fallback provider on failure
            **kwargs: Additional parameters
            
        Returns:
            Analysis results
        """
        try:
            # Prepare image data
            image_data = self._prepare_image_data(image_input)
            
            # Check cache first
            if self.cache:
                provider_name = provider or self.primary_provider
                cached_result = self.cache.get(image_data, prompt, provider_name)
                if cached_result:
                    logger.info("Using cached vision analysis result")
                    return cached_result
            
            # Get provider
            vision_provider = self._get_provider(provider)
            provider_name = provider or self.primary_provider
            
            # Perform analysis
            result = vision_provider.analyze_image(image_data, prompt, **kwargs)
            
            # If primary provider fails and fallback is enabled
            if not result.get("success") and use_fallback and self.fallback_provider:
                logger.warning(f"Primary provider failed, trying fallback: {self.fallback_provider}")
                fallback_provider = self._get_provider(self.fallback_provider)
                result = fallback_provider.analyze_image(image_data, prompt, **kwargs)
                provider_name = self.fallback_provider
            
            # Cache successful results
            if self.cache and result.get("success"):
                self.cache.set(image_data, prompt, provider_name, result)
            
            # Add metadata
            result["timestamp"] = datetime.now().isoformat()
            result["provider_used"] = provider_name
            
            return result
            
        except Exception as e:
            logger.error(f"Error in vision analysis: {e}")
            return {
                "provider": provider or self.primary_provider,
                "analysis": "",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def extract_text(self, 
                    image_input: Union[str, bytes, Path],
                    provider: str = None,
                    **kwargs) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image_input: Image data (URL, file path, or bytes)
            provider: Specific provider to use
            **kwargs: Additional parameters
            
        Returns:
            Extracted text
        """
        try:
            image_data = self._prepare_image_data(image_input)
            vision_provider = self._get_provider(provider)
            
            return vision_provider.extract_text(image_data, **kwargs)
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def describe_image(self, 
                      image_input: Union[str, bytes, Path],
                      provider: str = None,
                      **kwargs) -> str:
        """
        Generate detailed description of image.
        
        Args:
            image_input: Image data (URL, file path, or bytes)
            provider: Specific provider to use
            **kwargs: Additional parameters
            
        Returns:
            Image description
        """
        try:
            image_data = self._prepare_image_data(image_input)
            vision_provider = self._get_provider(provider)
            
            return vision_provider.describe_image(image_data, **kwargs)
            
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return ""
    
    def batch_analyze(self, 
                     images: List[Union[str, bytes, Path]],
                     prompt: str,
                     provider: str = None,
                     **kwargs) -> List[Dict[str, Any]]:
        """
        Analyze multiple images with the same prompt.
        
        Args:
            images: List of image inputs
            prompt: Analysis prompt
            provider: Specific provider to use
            **kwargs: Additional parameters
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i, image_input in enumerate(images):
            logger.info(f"Analyzing image {i+1}/{len(images)}")
            result = self.analyze_image(image_input, prompt, provider, **kwargs)
            results.append(result)
        
        return results
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        status = {}
        
        for provider_name, provider in self.providers.items():
            try:
                # Test with a simple analysis
                test_result = provider.analyze_image(
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                    "Test prompt",
                    max_tokens=10
                )
                status[provider_name] = {
                    "available": True,
                    "model": getattr(provider, 'model', 'unknown'),
                    "test_success": test_result.get("success", False)
                }
            except Exception as e:
                status[provider_name] = {
                    "available": False,
                    "error": str(e)
                }
        
        return status
