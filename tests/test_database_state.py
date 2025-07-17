#!/usr/bin/env python3
"""
Test that the database is working and has the electrical plan
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chromadb
from chromadb.config import Settings as ChromaSettings

def test_database_state():
    """Test the current database state"""
    print("=== TESTING DATABASE STATE ===\n")
    
    try:
        client = chromadb.PersistentClient(
            path="data/chroma_db",
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        collection = client.get_collection("canvas_multimodal")
        
        # Get all documents
        all_docs = collection.get()
        print(f"Total documents: {len(all_docs['ids'])}")
        
        # Check for vision analysis
        vision_count = 0
        image_count = 0
        electrical_found = False
        
        for i, doc in enumerate(all_docs['documents']):
            metadata = all_docs['metadatas'][i]
            
            if doc.startswith('[Image:'):
                image_count += 1
                if 'vision_analysis' in metadata:
                    vision_count += 1
            
            # Check for electrical plan
            if '16-1421-312f BG T2 electrical plan_Redacted.jpg' in doc:
                electrical_found = True
                print(f"✅ Found electrical plan at index {i}")
                print(f"   Document: {doc}")
                print(f"   Metadata keys: {sorted(metadata.keys())}")
                print(f"   Has vision_analysis: {'vision_analysis' in metadata}")
                if 'vision_analysis' in metadata:
                    print(f"   Vision analysis length: {len(metadata['vision_analysis'])}")
                    print(f"   Vision analysis preview: {metadata['vision_analysis'][:200]}...")
        
        print(f"\nSummary:")
        print(f"  Total documents: {len(all_docs['ids'])}")
        print(f"  Images with vision analysis: {vision_count}/{image_count}")
        print(f"  Electrical plan found: {'✅' if electrical_found else '❌'}")
        
        if electrical_found and vision_count > 0:
            print("\n✅ Database is ready for vision queries!")
        else:
            print("\n❌ Database issues detected")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_database_state()
