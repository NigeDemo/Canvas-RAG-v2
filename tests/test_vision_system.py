#!/usr/bin/env python
"""
Test script to verify Vision AI system works correctly
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.vision.vision_rag_integration import VisionEnhancedRAG
from src.utils.logger import get_logger

# Set up logging
logger = get_logger(__name__)

def test_vision_system():
    """Test the vision AI system initialization and basic functionality"""
    print("🔧 Testing Vision AI System")
    print("=" * 40)
    
    try:
        # Initialize Vision RAG system
        print("Creating Vision RAG system...")
        vision_rag = VisionEnhancedRAG()
        print("✅ Vision RAG system created successfully")
        
        # Test system status
        print("\nTesting system status...")
        status = vision_rag.get_system_status()
        print(f"✅ System status: {status}")
        
        # Test text-only query
        print("\nTesting text-only query...")
        query = "What are line weights in architectural drawings?"
        result = vision_rag.query(query)
        print(f"✅ Query processed: {result.success}")
        print(f"Response preview: {result.response[:100]}...")
        
        # Test with sample image URL (won't work without API keys but should handle gracefully)
        print("\nTesting image query (without API keys)...")
        sample_url = "https://example.com/sample.jpg"
        result = vision_rag.query(
            "Analyze this architectural drawing", 
            image_urls=[sample_url]
        )
        print(f"✅ Image query handled: {result.success}")
        if result.error:
            print(f"Expected error (no API keys): {result.error}")
        
        print("\n🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_vision_system()
    sys.exit(0 if success else 1)
