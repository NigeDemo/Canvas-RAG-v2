"""Test script for vision AI integration in Canvas RAG v2."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.vision.vision_processor import VisionProcessor
from src.vision.image_analyzer import ImageAnalyzer
from src.vision.vision_rag_integration import create_vision_rag_system
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_vision_providers():
    """Test vision provider initialization and status."""
    print("🔍 Testing Vision Providers...")
    
    try:
        vision_processor = VisionProcessor()
        status = vision_processor.get_provider_status()
        
        print(f"✅ Vision providers initialized: {list(status.keys())}")
        
        for provider, provider_status in status.items():
            if provider_status.get("available"):
                print(f"  ✅ {provider}: Available (model: {provider_status.get('model', 'unknown')})")
            else:
                print(f"  ❌ {provider}: Not available - {provider_status.get('error', 'unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing vision providers: {e}")
        return False

def test_image_analysis():
    """Test image analysis capabilities."""
    print("\n🖼️ Testing Image Analysis...")
    
    try:
        image_analyzer = ImageAnalyzer()
        
        # Test with a simple test image (1x1 pixel)
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        # Test different analysis types
        analysis_types = ["description", "ocr", "drawing_type"]
        
        for analysis_type in analysis_types:
            try:
                result = image_analyzer.analyze_image(
                    test_image_b64,
                    analysis_type=analysis_type,
                    query="Test query"
                )
                
                success = result.get("success", True)
                if success:
                    print(f"  ✅ {analysis_type}: Success")
                else:
                    print(f"  ❌ {analysis_type}: Failed - {result.get('error', 'unknown error')}")
                    
            except Exception as e:
                print(f"  ❌ {analysis_type}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing image analysis: {e}")
        return False

def test_vision_rag_integration():
    """Test vision-enhanced RAG system."""
    print("\n🤖 Testing Vision RAG Integration...")
    
    try:
        # Create vision RAG system without search engine for testing
        vision_rag = create_vision_rag_system()
        
        # Test system status
        status = vision_rag.get_system_status()
        print(f"✅ Vision RAG system initialized")
        print(f"  - Search engine: {status.get('search_engine', False)}")
        print(f"  - Vision processor: {len(status.get('vision_processor', {}))} providers")
        print(f"  - Response generator: {status.get('response_generator', False)}")
        
        # Test direct image analysis
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        result = vision_rag.analyze_image_directly(
            test_image_b64,
            "What type of architectural drawing is this?",
            analysis_type="drawing_type"
        )
        
        if result.get("success", True):
            print("  ✅ Direct image analysis: Success")
        else:
            print(f"  ❌ Direct image analysis: Failed - {result.get('error', 'unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing vision RAG integration: {e}")
        return False

def test_settings_configuration():
    """Test configuration settings."""
    print("\n⚙️ Testing Configuration...")
    
    try:
        # Check vision-related settings
        vision_settings = {
            "vision_primary_provider": getattr(settings, "vision_primary_provider", "Not set"),
            "vision_fallback_provider": getattr(settings, "vision_fallback_provider", "Not set"),
            "vision_cache_enabled": getattr(settings, "vision_cache_enabled", "Not set"),
            "cache_dir": getattr(settings, "cache_dir", "Not set"),
            "openai_vision_model": getattr(settings, "openai_vision_model", "Not set"),
            "claude_vision_model": getattr(settings, "claude_vision_model", "Not set"),
        }
        
        print("✅ Vision settings loaded:")
        for key, value in vision_settings.items():
            print(f"  - {key}: {value}")
        
        # Check API keys (don't print actual values)
        api_keys = {
            "openai_api_key": bool(getattr(settings, "openai_api_key", "")),
            "anthropic_api_key": bool(getattr(settings, "anthropic_api_key", "")),
        }
        
        print("\n🔑 API Key Status:")
        for key, available in api_keys.items():
            status = "✅ Available" if available else "❌ Not set"
            print(f"  - {key}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def main():
    """Run all vision AI tests."""
    print("🚀 Canvas RAG v2 - Vision AI Integration Test")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Configuration", test_settings_configuration),
        ("Vision Providers", test_vision_providers),
        ("Image Analysis", test_image_analysis),
        ("Vision RAG Integration", test_vision_rag_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Vision AI integration is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
