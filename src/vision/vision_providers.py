"""Vision AI providers for different vision models."""

from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
import base64
import json
from io import BytesIO
from PIL import Image

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

class VisionProvider(ABC):
    """Abstract base class for vision AI providers."""
    
    @abstractmethod
    def analyze_image(self, image_data: Union[str, bytes], prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze image content with a specific prompt.
        
        Args:
            image_data: Base64 encoded image string or raw bytes
            prompt: Analysis prompt
            **kwargs: Additional parameters
            
        Returns:
            Analysis results dictionary
        """
        pass
    
    @abstractmethod
    def extract_text(self, image_data: Union[str, bytes], **kwargs) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image_data: Base64 encoded image string or raw bytes
            **kwargs: Additional parameters
            
        Returns:
            Extracted text
        """
        pass
    
    @abstractmethod
    def describe_image(self, image_data: Union[str, bytes], **kwargs) -> str:
        """
        Generate detailed description of image content.
        
        Args:
            image_data: Base64 encoded image string or raw bytes
            **kwargs: Additional parameters
            
        Returns:
            Image description
        """
        pass

class OpenAIVisionProvider(VisionProvider):
    """OpenAI GPT-4 Vision provider."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize OpenAI Vision provider.
        
        Args:
            api_key: OpenAI API key
            model: Vision model name
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package is required for OpenAI Vision")
        
        self.client = openai.OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.openai_vision_model or "gpt-4o"
        
        logger.info(f"Initialized OpenAI Vision provider with model: {self.model}")
    
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
            return 'png'  # Default fallback

    def analyze_image(self, image_data: Union[str, bytes], prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze image content with GPT-4 Vision.
        
        Args:
            image_data: Base64 encoded image or raw bytes
            prompt: Analysis prompt
            **kwargs: Additional parameters
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Prepare image data
            if isinstance(image_data, bytes):
                image_format = self._detect_image_format(image_data)
                try:
                    image_b64 = base64.b64encode(image_data).decode('utf-8')
                except Exception as e:
                    logger.error(f"Error encoding image to base64: {e}")
                    raise ValueError(f"Failed to encode image data: {e}")
            else:
                image_format = 'png'  # Default for pre-encoded strings
                image_b64 = image_data
                # Validate base64 string
                try:
                    base64.b64decode(image_b64)
                except Exception as e:
                    logger.error(f"Invalid base64 image data: {e}")
                    raise ValueError(f"Invalid base64 image data: {e}")
            
            # Validate image_b64 is not empty
            if not image_b64:
                raise ValueError("Empty image data")
            
            # Create vision prompt with correct MIME type
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_format};base64,{image_b64}",
                            "detail": kwargs.get("detail", "high")
                        }
                    }
                ]
            }]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.3)
            )
            
            content = response.choices[0].message.content
            
            return {
                "provider": "openai",
                "model": self.model,
                "analysis": content,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image with OpenAI Vision: {e}")
            return {
                "provider": "openai",
                "model": self.model,
                "analysis": "",
                "error": str(e),
                "success": False
            }
    
    def extract_text(self, image_data: Union[str, bytes], **kwargs) -> str:
        """
        Extract text from image using GPT-4 Vision OCR.
        
        Args:
            image_data: Base64 encoded image or raw bytes
            **kwargs: Additional parameters
            
        Returns:
            Extracted text
        """
        ocr_prompt = """Extract all text from this image. Focus on:
1. Architectural annotations and dimensions
2. Title blocks and labels
3. Room names and identifiers
4. Scale indicators
5. Any technical specifications

Return only the text content, preserving the spatial relationships where possible."""
        
        result = self.analyze_image(image_data, ocr_prompt, **kwargs)
        return result.get("analysis", "") if result.get("success") else ""
    
    def describe_image(self, image_data: Union[str, bytes], **kwargs) -> str:
        """
        Generate detailed description of architectural drawing.
        
        Args:
            image_data: Base64 encoded image or raw bytes
            **kwargs: Additional parameters
            
        Returns:
            Image description
        """
        description_prompt = """Analyze this architectural drawing and provide a detailed description including:

1. Drawing type (floor plan, elevation, section, detail, etc.)
2. Scale and dimensions if visible
3. Key architectural elements (walls, doors, windows, etc.)
4. Room layouts and spatial relationships
5. Construction details and materials
6. Annotations and technical specifications
7. Any symbols or hatching patterns

Be specific and technical in your analysis."""
        
        result = self.analyze_image(image_data, description_prompt, **kwargs)
        return result.get("analysis", "") if result.get("success") else ""

class ClaudeVisionProvider(VisionProvider):
    """Anthropic Claude Vision provider."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Claude Vision provider.
        
        Args:
            api_key: Anthropic API key
            model: Claude model name
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package is required for Claude Vision")
        
        # Check if API key is available
        api_key = api_key or settings.anthropic_api_key
        if not api_key:
            raise ValueError("Anthropic API key is required for Claude Vision")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model or settings.claude_vision_model or "claude-3-5-sonnet-20241022"
        
        logger.info(f"Initialized Claude Vision provider with model: {self.model}")
    
    def analyze_image(self, image_data: Union[str, bytes], prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze image content with Claude Vision.
        
        Args:
            image_data: Base64 encoded image or raw bytes
            prompt: Analysis prompt
            **kwargs: Additional parameters
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Prepare image data
            if isinstance(image_data, bytes):
                image_b64 = base64.b64encode(image_data).decode('utf-8')
            else:
                image_b64 = image_data
            
            # Create vision message
            message = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.3),
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            content = message.content[0].text if message.content else ""
            
            return {
                "provider": "claude",
                "model": self.model,
                "analysis": content,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens if message.usage else 0,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image with Claude Vision: {e}")
            return {
                "provider": "claude",
                "model": self.model,
                "analysis": "",
                "error": str(e),
                "success": False
            }
    
    def extract_text(self, image_data: Union[str, bytes], **kwargs) -> str:
        """
        Extract text from image using Claude Vision OCR.
        
        Args:
            image_data: Base64 encoded image or raw bytes
            **kwargs: Additional parameters
            
        Returns:
            Extracted text
        """
        ocr_prompt = """Please extract all text visible in this architectural drawing. Include:
- Dimensions and measurements
- Room labels and identifiers
- Technical annotations
- Title block information
- Scale indicators
- Material specifications

Preserve the spatial organization of the text where possible."""
        
        result = self.analyze_image(image_data, ocr_prompt, **kwargs)
        return result.get("analysis", "") if result.get("success") else ""
    
    def describe_image(self, image_data: Union[str, bytes], **kwargs) -> str:
        """
        Generate detailed description of architectural drawing.
        
        Args:
            image_data: Base64 encoded image or raw bytes
            **kwargs: Additional parameters
            
        Returns:
            Image description
        """
        description_prompt = """Analyze this architectural drawing comprehensively. Describe:

1. Type of drawing (plan, elevation, section, detail, perspective)
2. Scale and dimensional information
3. Architectural elements (walls, openings, structural components)
4. Spatial organization and room layouts
5. Construction details and material indications
6. Annotation systems and symbols used
7. Technical specifications visible
8. Drawing conventions and standards followed

Provide a detailed, technical analysis suitable for architecture education."""
        
        result = self.analyze_image(image_data, description_prompt, **kwargs)
        return result.get("analysis", "") if result.get("success") else ""

def get_vision_provider(provider_name: str = "openai", **kwargs) -> VisionProvider:
    """
    Factory function to get vision provider instance.
    
    Args:
        provider_name: Name of the provider ('openai' or 'claude')
        **kwargs: Additional parameters for provider initialization
        
    Returns:
        Vision provider instance
    """
    if provider_name.lower() == "openai":
        return OpenAIVisionProvider(**kwargs)
    elif provider_name.lower() == "claude":
        return ClaudeVisionProvider(**kwargs)
    else:
        raise ValueError(f"Unknown vision provider: {provider_name}")
