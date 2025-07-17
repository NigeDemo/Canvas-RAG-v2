#!/usr/bin/env python3
"""Test script to verify image processing fixes."""

import sys
import os
from pathlib import Path
from io import BytesIO
import base64
from PIL import Image, ImageDraw

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.vision.vision_providers import OpenAIVisionProvider
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

def create_test_image() -> bytes:
    """Create a simple test image."""
    # Create a simple test image
    image = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Test Image", fill='black')
    draw.rectangle([50, 30, 150, 70], outline='blue', width=2)
    
    # Save to bytes
    img_buffer = BytesIO()
    image.save(img_buffer, format='PNG')
    return img_buffer.getvalue()

def test_image_format_detection():
    """Test image format detection."""
    print("🔍 Testing image format detection...")
    
    provider = OpenAIVisionProvider()
    
    # Test different formats
    test_cases = [
        (b'\xff\xd8\xff', 'jpeg'),
        (b'\x89PNG\r\n\x1a\n', 'png'),
        (b'GIF87a', 'gif'),
        (b'GIF89a', 'gif'),
        (b'RIFF\x00\x00\x00\x00WEBP', 'webp'),
        (b'BM', 'bmp'),
        (b'\x00\x00\x00\x00', 'png'),  # Unknown format should default to png
    ]
    
    for test_data, expected_format in test_cases:
        detected_format = provider._detect_image_format(test_data)
        status = "✅" if detected_format == expected_format else "❌"
        print(f"{status} {test_data[:8]} -> {detected_format} (expected: {expected_format})")

def test_base64_encoding():
    """Test base64 encoding with actual image."""
    print("\n🔍 Testing base64 encoding...")
    
    # Create test image
    test_image_bytes = create_test_image()
    print(f"✅ Created test image: {len(test_image_bytes)} bytes")
    
    # Test base64 encoding
    try:
        encoded = base64.b64encode(test_image_bytes).decode('utf-8')
        print(f"✅ Base64 encoded: {len(encoded)} characters")
        
        # Verify it can be decoded
        decoded = base64.b64decode(encoded)
        print(f"✅ Base64 decoded: {len(decoded)} bytes")
        
        # Verify decoded matches original
        if decoded == test_image_bytes:
            print("✅ Base64 encoding/decoding successful")
        else:
            print("❌ Base64 encoding/decoding failed")
            
    except Exception as e:
        print(f"❌ Base64 encoding failed: {e}")

def test_vision_provider():
    """Test the OpenAI Vision provider with fixed image handling."""
    print("\n🔍 Testing OpenAI Vision provider...")
    
    # Check if API key is available
    if not settings.openai_api_key:
        print("❌ No OpenAI API key configured. Skipping vision provider test.")
        return
    
    try:
        provider = OpenAIVisionProvider()
        print("✅ OpenAI Vision provider initialized")
        
        # Create test image
        test_image_bytes = create_test_image()
        
        # Test image analysis
        result = provider.analyze_image(
            test_image_bytes,
            "Describe what you see in this image",
            max_tokens=50
        )
        
        if result.get('success'):
            print("✅ Vision analysis successful")
            print(f"Analysis: {result.get('analysis', '')[:100]}...")
        else:
            print(f"❌ Vision analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Vision provider test failed: {e}")

def main():
    """Run all tests."""
    print("🧪 Testing Image Processing Fixes")
    print("=" * 50)
    
    try:
        test_image_format_detection()
        test_base64_encoding()
        test_vision_provider()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
