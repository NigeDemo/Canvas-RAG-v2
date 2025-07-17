#!/usr/bin/env python
"""
Test Vision AI configuration with available API keys
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_vision_config():
    """Test vision AI configuration"""
    print("🔍 Testing Vision AI Configuration")
    print("=" * 50)
    
    # Test environment loading
    try:
        from src.config.settings import settings
        print("✅ Settings loaded successfully")
        
        # Check API keys
        print("\n🔑 API Key Status:")
        print(f"OpenAI API Key: {'✅ Configured' if settings.openai_api_key else '❌ Missing'}")
        print(f"Anthropic API Key: {'✅ Configured' if settings.anthropic_api_key else '❌ Missing'}")
        print(f"Google API Key: {'✅ Configured' if settings.google_api_key else '❌ Missing'}")
        
        # Check vision settings
        print("\n⚙️ Vision Settings:")
        print(f"Primary Provider: {settings.vision_primary_provider}")
        print(f"Fallback Provider: {settings.vision_fallback_provider}")
        print(f"OpenAI Vision Model: {settings.openai_vision_model}")
        print(f"Claude Vision Model: {settings.claude_vision_model}")
        
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
    
    # Test provider initialization
    print("\n🤖 Testing Provider Initialization:")
    
    # Test OpenAI provider
    try:
        from src.vision.vision_providers import OpenAIVisionProvider
        if settings.openai_api_key:
            provider = OpenAIVisionProvider()
            print("✅ OpenAI Vision Provider: Ready")
        else:
            print("❌ OpenAI Vision Provider: No API key")
    except Exception as e:
        print(f"❌ OpenAI Vision Provider Error: {e}")
    
    # Test Claude provider
    try:
        from src.vision.vision_providers import ClaudeVisionProvider
        if settings.anthropic_api_key:
            provider = ClaudeVisionProvider()
            print("✅ Claude Vision Provider: Ready")
        else:
            print("❌ Claude Vision Provider: No API key")
    except Exception as e:
        print(f"❌ Claude Vision Provider Error: {e}")
    
    # Test Vision Processor with OpenAI only
    print("\n🔄 Testing Vision Processor with OpenAI only:")
    try:
        from src.vision.vision_processor import VisionProcessor
        processor = VisionProcessor(
            primary_provider="openai",
            fallback_provider="openai",  # Use OpenAI as fallback too
            use_cache=True
        )
        print("✅ Vision Processor: Initialized successfully")
        print(f"Available providers: {list(processor.providers.keys())}")
        
        # Test system status
        print("\n📊 System Status Test:")
        from src.vision.vision_rag_integration import VisionEnhancedRAG
        vision_rag = VisionEnhancedRAG()
        status = vision_rag.get_system_status()
        print(f"✅ System Status: {status}")
        
    except Exception as e:
        print(f"❌ Vision Processor Error: {e}")
        return False
    
    print("\n🎉 Configuration test completed!")
    return True

if __name__ == "__main__":
    success = test_vision_config()
    if success:
        print("\n✅ Your vision AI system is properly configured!")
        print("💡 You can now restart the Streamlit app and try image analysis.")
    else:
        print("\n❌ Configuration issues detected. Please check the errors above.")
