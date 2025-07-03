#!/usr/bin/env python3

"""Debug script to check embedding dimensions and clear database if needed."""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.embeddings.multimodal_embeddings import EmbeddingManager
from src.indexing.vector_store import VectorStore
from src.utils.logger import get_logger
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = get_logger(__name__)

def check_embedding_dimensions():
    """Check the dimensions of different embedding models."""
    
    print("=== Checking Embedding Model Dimensions ===")
    
    # Test different embedding models
    models_to_test = [
        ("nomic", {}),
        ("openai", {"model_name": "text-embedding-3-large"}),
        ("openai", {"model_name": "text-embedding-ada-002"})
    ]
    
    for model_type, kwargs in models_to_test:
        try:
            print(f"\nTesting {model_type} model with {kwargs}")
            embedding_manager = EmbeddingManager(model_type=model_type, **kwargs)
            
            # Test with a simple text
            test_embedding = embedding_manager.embed_query("test text")
            print(f"  Dimensions: {len(test_embedding)}")
            print(f"  Shape: {test_embedding.shape}")
            
        except Exception as e:
            print(f"  Error: {e}")

def check_existing_database():
    """Check what's in the existing database."""
    
    print("\n=== Checking Existing Database ===")
    
    try:
        # Connect to existing database
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # List collections
        collections = client.list_collections()
        print(f"Found {len(collections)} collections:")
        
        for collection in collections:
            print(f"  Collection: {collection.name}")
            count = collection.count()
            print(f"  Document count: {count}")
            
            if count > 0:
                # Get a sample document to check embedding dimensions
                try:
                    sample = collection.get(limit=1, include=["embeddings"])
                    if sample["embeddings"] and len(sample["embeddings"]) > 0:
                        embedding = sample["embeddings"][0]
                        print(f"  Embedding dimensions: {len(embedding)}")
                    else:
                        print("  No embeddings found in sample")
                except Exception as e:
                    print(f"  Error getting sample: {e}")
    
    except Exception as e:
        print(f"Error accessing database: {e}")

def clear_database():
    """Clear the existing database."""
    
    print("\n=== Clearing Database ===")
    
    try:
        # Connect to existing database
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get collections and delete them
        collections = client.list_collections()
        for collection in collections:
            print(f"Deleting collection: {collection.name}")
            client.delete_collection(collection.name)
        
        print("Database cleared successfully")
        
    except Exception as e:
        print(f"Error clearing database: {e}")

def main():
    """Main function."""
    
    check_embedding_dimensions()
    check_existing_database()
    
    # Ask if user wants to clear the database
    response = input("\nDo you want to clear the existing database? (y/N): ")
    if response.lower() in ['y', 'yes']:
        clear_database()
        print("\nDatabase cleared. You can now re-run the indexing process.")
    else:
        print("\nDatabase preserved. The dimension mismatch issue may persist.")

if __name__ == "__main__":
    main()
