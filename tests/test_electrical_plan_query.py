#!/usr/bin/env python3
"""
Test the complete query pipeline to see what's happening with electrical plan queries
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chromadb
from chromadb.config import Settings as ChromaSettings

def test_electrical_plan_query():
    """Test the complete pipeline for electrical plan queries"""
    print("=== TESTING ELECTRICAL PLAN QUERY PIPELINE ===\n")
    
    try:
        # Step 1: Check what's in ChromaDB
        print("1. CHECKING CHROMADB CONTENT:")
        client = chromadb.PersistentClient(
            path="data/chroma_db",
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        collection = client.get_collection("canvas_multimodal")
        
        # Search for electrical plan directly
        print("   Searching for 'electrical plan'...")
        search_results = collection.query(
            query_texts=["electrical plan"],
            n_results=5
        )
        
        print(f"   Found {len(search_results['documents'][0])} results")
        
        for i, doc in enumerate(search_results['documents'][0]):
            metadata = search_results['metadatas'][0][i]
            print(f"   Result {i+1}: {doc[:100]}...")
            print(f"     - Has vision_analysis: {'vision_analysis' in metadata}")
            if 'vision_analysis' in metadata:
                print(f"     - Vision analysis length: {len(metadata['vision_analysis'])}")
                print(f"     - Vision analysis preview: {metadata['vision_analysis'][:200]}...")
            print()
        
        # Step 2: Check specific electrical plan document
        print("2. CHECKING SPECIFIC ELECTRICAL PLAN:")
        all_docs = collection.get()
        
        electrical_found = False
        for i, doc in enumerate(all_docs['documents']):
            if '16-1421-312f BG T2 electrical plan_Redacted.jpg' in doc:
                print(f"   Found electrical plan at index {i}")
                print(f"   Document: {doc}")
                metadata = all_docs['metadatas'][i]
                print(f"   Metadata keys: {sorted(metadata.keys())}")
                print(f"   Has vision_analysis: {'vision_analysis' in metadata}")
                if 'vision_analysis' in metadata:
                    print(f"   Vision analysis length: {len(metadata['vision_analysis'])}")
                    print(f"   Vision analysis content: {metadata['vision_analysis'][:300]}...")
                electrical_found = True
                break
        
        if not electrical_found:
            print("   ❌ Electrical plan not found in database")
        
        # Step 3: Test query matching
        print("3. TESTING QUERY MATCHING:")
        test_queries = [
            "electrical plan",
            "16-1421-312f BG T2 electrical plan",
            "electrical",
            "describe the electrical plan"
        ]
        
        for query in test_queries:
            print(f"   Testing query: '{query}'")
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            electrical_in_results = False
            for j, doc in enumerate(results['documents'][0]):
                if '16-1421-312f BG T2 electrical plan_Redacted.jpg' in doc:
                    print(f"     ✅ Electrical plan found at position {j+1}")
                    metadata = results['metadatas'][0][j]
                    print(f"     Has vision_analysis: {'vision_analysis' in metadata}")
                    electrical_in_results = True
                    break
            
            if not electrical_in_results:
                print(f"     ❌ Electrical plan not in top 3 results")
                print(f"     Top result: {results['documents'][0][0][:100]}...")
        
        print("\n4. SUMMARY:")
        print(f"   Total documents in database: {len(all_docs['documents'])}")
        
        # Count images with vision analysis
        images_with_vision = 0
        total_images = 0
        for i, doc in enumerate(all_docs['documents']):
            if doc.startswith('[Image:'):
                total_images += 1
                if 'vision_analysis' in all_docs['metadatas'][i]:
                    images_with_vision += 1
        
        print(f"   Images with vision analysis: {images_with_vision}/{total_images}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_electrical_plan_query()
