#!/usr/bin/env python3
"""
Check database status and rebuild if needed
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chromadb
from chromadb.config import Settings as ChromaSettings

def check_database_status():
    """Check if database needs rebuilding"""
    print("=== CHECKING DATABASE STATUS ===")
    
    try:
        client = chromadb.PersistentClient(
            path='data/chroma_db',
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        collections = client.list_collections()
        if collections:
            collection = client.get_collection('canvas_multimodal')
            result = collection.get()
            print(f'Database has {len(result["ids"])} documents')
            
            # Check if it has vision analysis
            vision_count = 0
            for metadata in result['metadatas']:
                if 'vision_analysis' in metadata:
                    vision_count += 1
            
            print(f'Documents with vision analysis: {vision_count}')
            
            if len(result["ids"]) > 0:
                print("✅ Database has content")
                return True
            else:
                print("❌ Database is empty")
                return False
        else:
            print('❌ No collections found - database is empty')
            return False
    except Exception as e:
        print(f'❌ Database error: {e}')
        return False

def rebuild_index():
    """Rebuild the index from processed content"""
    print("\n=== REBUILDING INDEX ===")
    
    try:
        # Check if processed content exists
        from pathlib import Path
        processed_file = Path("data/processed/processed_page_construction_drawing_package_2_metadata.json")
        
        if not processed_file.exists():
            print("❌ No processed content found")
            return False
        
        print(f"✅ Found processed content: {processed_file}")
        
        # Import and create IndexBuilder with the correct embedding model
        from indexing.vector_store import IndexBuilder
        
        # Use openai model to match what was used originally
        print("Creating IndexBuilder with 'openai' embedding model...")
        index_builder = IndexBuilder(embedding_model_type="openai")
        
        # Build the index
        print("Building index...")
        index_builder.build_index(processed_file)
        
        print("✅ Index rebuilt successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to rebuild index: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    needs_rebuild = not check_database_status()
    
    if needs_rebuild:
        print("\nDatabase needs rebuilding...")
        success = rebuild_index()
        if success:
            print("\n✅ Index rebuild complete")
            check_database_status()
        else:
            print("\n❌ Index rebuild failed")
    else:
        print("\n✅ Database is ready to use")
