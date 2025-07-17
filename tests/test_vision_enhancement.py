#!/usr/bin/env python3
"""Test the vision enhancement specifically"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test mimicking the Streamlit call
from src.indexing.vector_store import IndexBuilder
from src.vision.vision_rag_integration import VisionEnhancedRAG

def test_vision_enhancement():
    """Test vision enhancement with debug output"""
    
    print("Initializing VisionEnhancedRAG system...")
    
    # Initialize the system with search engine (like Streamlit does)
    from src.vision.vision_rag_integration import create_vision_rag_system
    from src.indexing.vector_store import IndexBuilder
    from src.retrieval.hybrid_search import HybridSearchEngine
    
    # Create search engine the same way as Streamlit
    index_builder = IndexBuilder(embedding_model_type="openai")
    retriever = index_builder.get_retriever()
    search_engine = HybridSearchEngine(retriever)
    
    vision_rag = create_vision_rag_system(search_engine)
    
    # Test query (mimicking Streamlit)
    query = "Can you describe the electrical plan"
    print(f"Testing query: {query}")
    
    # Process query with vision enabled (mimicking Streamlit)
    result = vision_rag.query(
        query,
        enable_vision=True,
        max_images=3
    )
    
    print(f"Result success: {result.success}")
    print(f"Response length: {len(result.response)}")
    print(f"Response preview: {result.response[:200]}...")
    print(f"Vision analyses: {len(result.vision_analyses)}")
    
    return result

if __name__ == "__main__":
    test_vision_enhancement()
