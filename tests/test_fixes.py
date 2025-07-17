#!/usr/bin/env python3
"""Quick test to verify vision AI fixes work correctly."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_vision_rag_initialization():
    """Test that vision RAG system can be initialized without errors."""
    print("Testing Vision RAG initialization...")
    
    try:
        from src.vision.vision_rag_integration import create_vision_rag_system
        
        # Test creating system without search engine
        vision_rag = create_vision_rag_system()
        print("✅ Vision RAG system created successfully")
        
        # Test system status
        status = vision_rag.get_system_status()
        print(f"✅ System status retrieved: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing vision RAG: {e}")
        return False

def test_text_only_query():
    """Test that text-only queries work without search engine."""
    print("\nTesting text-only query without search engine...")
    
    try:
        from src.vision.vision_rag_integration import create_vision_rag_system
        
        # Create system without search engine
        vision_rag = create_vision_rag_system()
        
        # Test query
        result = vision_rag.query(
            "What are line weights in architectural drawings?",
            enable_vision=False
        )
        
        print(f"✅ Query processed successfully")
        print(f"Response: {result.response[:100]}...")
        print(f"Success: {result.success}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Error in text-only query: {e}")
        return False

def test_vision_enhanced_generator():
    """Test that vision enhanced generator can be created."""
    print("\nTesting Vision Enhanced Generator...")
    
    try:
        from src.generation.vision_enhanced_generator import VisionEnhancedResponseGenerator
        
        # Create generator without LLM provider
        generator = VisionEnhancedResponseGenerator()
        print("✅ Vision Enhanced Generator created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating vision enhanced generator: {e}")
        return False

def main():
    """Run all tests."""
    print("🔧 Testing Vision AI Fixes")
    print("=" * 40)
    
    tests = [
        ("Vision RAG Initialization", test_vision_rag_initialization),
        ("Text-only Query", test_text_only_query),
        ("Vision Enhanced Generator", test_vision_enhanced_generator),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fixes working correctly!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
