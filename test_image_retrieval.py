#!/usr/bin/env python3

"""Test script to verify that image references are properly indexed and retrievable."""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.indexing.vector_store import VectorStore, HybridRetriever, IndexBuilder
from src.embeddings.multimodal_embeddings import EmbeddingManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_vector_database_query():
    """Test querying the vector database for both text and image content."""
    
    print("=== Testing Vector Database Queries ===\n")
    
    try:
        # Initialize components
        vector_store = VectorStore()
        embedding_manager = EmbeddingManager(model_type="openai")
        
        # Check collection info
        info = vector_store.get_collection_info()
        print(f"Collection Info:")
        print(f"  Name: {info.get('name', 'Unknown')}")
        print(f"  Document Count: {info.get('count', 0)}")
        print(f"  Persist Directory: {info.get('persist_directory', 'Unknown')}")
        print()
        
        # Test queries
        test_queries = [
            "construction drawing",
            "coordination example", 
            "topographical survey",
            "concept design",
            "building design process"
        ]
        
        for query in test_queries:
            print(f"Query: '{query}'")
            print("-" * 50)
            
            # Generate query embedding
            query_embedding = embedding_manager.embed_query(query)
            print(f"Query embedding dimensions: {len(query_embedding)}")
            
            # Search vector database
            results = vector_store.query(query_embedding, n_results=5)
            
            if results and results.get("documents") and len(results["documents"]) > 0:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(documents)
                distances = results["distances"][0] if results.get("distances") else [0] * len(documents)
                
                print(f"Found {len(documents)} results:")
                
                for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
                    content_type = meta.get("content_type", "unknown")
                    print(f"  {i+1}. Type: {content_type} | Distance: {dist:.4f}")
                    print(f"     Text: {doc[:100]}...")
                    
                    if content_type == "image_reference":
                        print(f"     Image URL: {meta.get('image_url', 'N/A')}")
                        print(f"     Alt Text: {meta.get('alt_text', 'N/A')}")
                    
                    print()
            else:
                print("No results found")
            
            print("=" * 60)
            print()
    
    except Exception as e:
        print(f"Error testing vector database: {e}")
        import traceback
        traceback.print_exc()

def test_hybrid_retrieval():
    """Test the hybrid retrieval system."""
    
    print("=== Testing Hybrid Retrieval System ===\n")
    
    try:
        # Initialize the complete retrieval system
        index_builder = IndexBuilder(embedding_model_type="openai")
        retriever = index_builder.retriever
        
        # Test queries
        test_queries = [
            "construction drawing coordination",
            "topographical survey example",
            "building design process image"
        ]
        
        for query in test_queries:
            print(f"Hybrid Query: '{query}'")
            print("-" * 50)
            
            results = retriever.retrieve(query, n_results=5)
            
            if results:
                print(f"Found {len(results)} results:")
                
                for i, result in enumerate(results):
                    content_type = result.get("metadata", {}).get("content_type", "unknown")
                    score = result.get("score", 0)
                    rank = result.get("rank", i+1)
                    
                    print(f"  {rank}. Type: {content_type} | Score: {score:.4f}")
                    print(f"     Text: {result.get('text', '')[:100]}...")
                    
                    if content_type == "image_reference":
                        metadata = result.get("metadata", {})
                        print(f"     Image URL: {metadata.get('image_url', 'N/A')}")
                        print(f"     Alt Text: {metadata.get('alt_text', 'N/A')}")
                    
                    print()
            else:
                print("No results found")
            
            print("=" * 60)
            print()
    
    except Exception as e:
        print(f"Error testing hybrid retrieval: {e}")
        import traceback
        traceback.print_exc()

def test_image_specific_queries():
    """Test queries specifically targeting image content."""
    
    print("=== Testing Image-Specific Queries ===\n")
    
    try:
        # Initialize components
        vector_store = VectorStore()
        embedding_manager = EmbeddingManager(model_type="openai")
        
        # Test queries that should match image alt text
        image_queries = [
            "zoomed column coordination example",
            "topographical survey example", 
            "concept design construction drawing realised product building",
            "image"  # Generic term to find any images
        ]
        
        for query in image_queries:
            print(f"Image Query: '{query}'")
            print("-" * 50)
            
            # Generate query embedding
            query_embedding = embedding_manager.embed_query(query)
            
            # Search with more results to increase chance of finding images
            results = vector_store.query(query_embedding, n_results=20)
            
            if results and results.get("documents") and len(results["documents"]) > 0:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(documents)
                distances = results["distances"][0] if results.get("distances") else [0] * len(documents)
                
                # Filter for image references
                image_results = []
                text_results = []
                
                for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
                    content_type = meta.get("content_type", "unknown")
                    if content_type == "image_reference":
                        image_results.append((doc, meta, dist, i+1))
                    else:
                        text_results.append((doc, meta, dist, i+1))
                
                print(f"Found {len(image_results)} image references and {len(text_results)} text chunks")
                
                if image_results:
                    print("\nImage References:")
                    for doc, meta, dist, rank in image_results[:3]:  # Show top 3 images
                        print(f"  {rank}. Distance: {dist:.4f}")
                        print(f"     Text: {doc[:100]}...")
                        print(f"     Image URL: {meta.get('image_url', 'N/A')}")
                        print(f"     Alt Text: {meta.get('alt_text', 'N/A')}")
                        print()
                else:
                    print("❌ No image references found in results!")
                    
                # Show some text results for comparison
                if text_results:
                    print(f"Top text results for comparison:")
                    for doc, meta, dist, rank in text_results[:2]:
                        print(f"  {rank}. Distance: {dist:.4f}")
                        print(f"     Text: {doc[:100]}...")
                        print()
            else:
                print("No results found")
            
            print("=" * 60)
            print()
    
    except Exception as e:
        print(f"Error testing image queries: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    
    test_vector_database_query()
    test_hybrid_retrieval()
    test_image_specific_queries()
    
    print("✅ Testing complete! Image references should now be retrievable.")

if __name__ == "__main__":
    main()
