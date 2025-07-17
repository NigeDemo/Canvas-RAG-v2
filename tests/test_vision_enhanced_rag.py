#!/usr/bin/env python3
"""Test the VisionEnhancedRAG system directly."""

import sys
sys.path.append('src')

from retrieval.hybrid_search import HybridSearchEngine
from vision.vision_rag_integration import VisionEnhancedRAG

def test_vision_enhanced_rag():
    """Test the VisionEnhancedRAG system with electrical plan query."""
    
    # Initialize the system
    print("Initializing VisionEnhancedRAG...")
    vision_rag = VisionEnhancedRAG()
    
    # Test query
    query = "Can you describe the electrical plan"
    
    print(f"Testing query: {query}")
    
    # Process query
    try:
        result = vision_rag.process_query(query)
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vision_enhanced_rag()
