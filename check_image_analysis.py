#!/usr/bin/env python3
"""Check what image references look like in the vector database."""

from src.indexing.vector_store import IndexBuilder

def check_image_analysis():
    print("Checking image analysis in vector database...")
    
    # Initialize system
    ib = IndexBuilder(embedding_model_type="openai")
    retriever = ib.get_retriever()
    
    # Query for image references
    results = retriever.vector_store.query(
        retriever.embedding_manager.embed_query("image"),
        n_results=3,
        where={"content_type": "image_reference"}
    )
    
    if results['documents'] and results['documents'][0]:
        print("\nSample image reference:")
        print(f"Text: {results['documents'][0][0]}")
        print(f"Metadata: {results['metadatas'][0][0]}")
        
        # Check if there are any analysis fields
        metadata = results['metadatas'][0][0]
        print(f"\nAvailable metadata keys: {list(metadata.keys())}")
        
        # Look for any vision/analysis related fields
        analysis_fields = [k for k in metadata.keys() if any(word in k.lower() for word in ['vision', 'analysis', 'description', 'content', 'caption'])]
        if analysis_fields:
            print(f"Analysis-related fields: {analysis_fields}")
            for field in analysis_fields:
                print(f"  {field}: {metadata[field]}")
        else:
            print("No image analysis fields found in metadata")
            
        # Show what we do have
        print(f"\nImage URL: {metadata.get('image_url', 'N/A')}")
        print(f"Alt text: {metadata.get('alt_text', 'N/A')}")
        print(f"Title: {metadata.get('title', 'N/A')}")
    else:
        print("No image references found")

if __name__ == "__main__":
    check_image_analysis()
