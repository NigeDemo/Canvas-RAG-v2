#!/usr/bin/env python3
"""Test script to check if image references are being retrieved."""

from src.indexing.vector_store import IndexBuilder

def test_image_retrieval():
    print("Testing image retrieval...")
    
    # Initialize system
    ib = IndexBuilder(embedding_model_type="openai")
    retriever = ib.get_retriever()
    
    # Test queries that should find images
    test_queries = [
        "show me any image",
        "image drawings diagrams", 
        "visual example",
        "Can you show me any image from the page"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing query: '{query}' ---")
        results = retriever.retrieve(query, n_results=10)
        print(f"Found {len(results)} results")
        
        image_count = 0
        for i, r in enumerate(results[:5]):
            content_type = r.get("metadata", {}).get("content_type", "unknown")
            text_preview = str(r.get("text", ""))[:100]
            print(f"  {i+1}. Type: {content_type} | Text: {text_preview}...")
            if content_type == "image_reference":
                image_count += 1
                url = r.get("metadata", {}).get("image_url", "No URL")
                print(f"      Image URL: {url}")
        
        print(f"  Images found: {image_count}")

if __name__ == "__main__":
    test_image_retrieval()
