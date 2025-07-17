#!/usr/bin/env python3
"""Test the updated vision-enabled chat system."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.indexing.vector_store import IndexBuilder

def test_vision_enabled_queries():
    """Test the vision-enabled query system."""
    
    print("=== Testing Vision-Enabled Query System ===\n")
    
    # Initialize system
    index_builder = IndexBuilder(embedding_model_type="openai")
    retriever = index_builder.get_retriever()
    
    # Test image queries
    test_queries = [
        "List all images on the page",
        "Show me construction drawing examples",
        "Describe a specific image of coordination details"
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        print("-" * 50)
        
        # Get results with increased n_results for image queries
        results = retriever.retrieve(query, n_results=20)
        
        # Count image references
        image_count = len([r for r in results if r.get("metadata", {}).get("content_type") == "image_reference"])
        text_count = len([r for r in results if r.get("metadata", {}).get("content_type") == "text_chunk"])
        
        print(f"Found {len(results)} total results:")
        print(f"  - {image_count} image references")
        print(f"  - {text_count} text chunks")
        
        # Show first few image references with vision analysis
        image_results = [r for r in results if r.get("metadata", {}).get("content_type") == "image_reference"]
        
        if image_results:
            print(f"\nFirst 3 image references:")
            for i, result in enumerate(image_results[:3]):
                metadata = result.get("metadata", {})
                vision_analysis = metadata.get("vision_analysis", "")
                drawing_type = metadata.get("drawing_type", "unknown")
                
                print(f"  {i+1}. {result.get('text', '')[:50]}...")
                print(f"     Drawing type: {drawing_type}")
                print(f"     Vision analysis: {vision_analysis[:100]}...")
                print(f"     Has vision analysis: {bool(vision_analysis)}")
                print()
        
        print("=" * 60)
        print()

if __name__ == "__main__":
    test_vision_enabled_queries()
