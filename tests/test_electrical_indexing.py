#!/usr/bin/env python3
"""
Test the indexing process with the electrical plan segment that HAS vision analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json
from pathlib import Path

def test_electrical_plan_indexing():
    """Test indexing specifically with the electrical plan that has vision analysis"""
    print("=== TESTING ELECTRICAL PLAN INDEXING ===\n")
    
    # Load processed content
    with open('data/processed/processed_page_construction_drawing_package_2_metadata.json', 'r', encoding='utf-8') as f:
        segments = json.load(f)
    
    # Find the electrical plan segment
    electrical_segment = None
    for i, seg in enumerate(segments):
        if seg.get('alt_text') == '16-1421-312f BG T2 electrical plan_Redacted.jpg':
            electrical_segment = seg
            break
    
    if not electrical_segment:
        print("❌ Electrical plan not found")
        return
    
    print("✅ Found electrical plan segment:")
    print(f"   - Alt text: {electrical_segment.get('alt_text')}")
    print(f"   - Keys: {sorted(electrical_segment.keys())}")
    print(f"   - Has vision_analysis: {'vision_analysis' in electrical_segment}")
    print(f"   - Vision analysis length: {len(electrical_segment.get('vision_analysis', ''))}")
    
    # Test ChromaDB storage with this segment
    print(f"\n=== TESTING CHROMADB STORAGE ===")
    
    # Prepare document as IndexBuilder would
    doc_text = f"[Image: {electrical_segment.get('alt_text', 'architectural drawing')}]"
    if electrical_segment.get('title'):
        doc_text += f" - {electrical_segment['title']}"
    
    print(f"Document text: {doc_text}")
    
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        print("Creating ChromaDB client...")
        client = chromadb.Client(settings=ChromaSettings(anonymized_telemetry=False))
        
        # Clean up any existing test collection
        try:
            client.delete_collection("test_electrical_plan")
        except:
            pass
        
        collection = client.create_collection("test_electrical_plan")
        
        print("Adding electrical plan with vision analysis...")
        collection.add(
            documents=[doc_text],
            metadatas=[electrical_segment],
            ids=["electrical_plan_test"]
        )
        
        print("✅ Document added successfully")
        
        # Retrieve and check what was stored
        print("Retrieving document...")
        result = collection.get(ids=["electrical_plan_test"])
        
        retrieved_metadata = result['metadatas'][0]
        
        print(f"Original keys: {sorted(electrical_segment.keys())}")
        print(f"Retrieved keys: {sorted(retrieved_metadata.keys())}")
        
        # Check for missing keys
        original_keys = set(electrical_segment.keys())
        retrieved_keys = set(retrieved_metadata.keys())
        missing_keys = original_keys - retrieved_keys
        
        if missing_keys:
            print(f"❌ MISSING KEYS: {missing_keys}")
            
            # Check each missing key
            for key in missing_keys:
                value = electrical_segment[key]
                print(f"   {key}:")
                print(f"     - Type: {type(value).__name__}")
                print(f"     - Length: {len(str(value))}")
                print(f"     - Value preview: {str(value)[:100]}...")
                
                # Test JSON serialization
                try:
                    json.dumps(value)
                    print(f"     - JSON serializable: ✅")
                except Exception as e:
                    print(f"     - JSON serializable: ❌ ({e})")
        else:
            print("✅ All keys preserved")
        
        # Check vision analysis specifically
        if 'vision_analysis' in retrieved_metadata:
            print(f"✅ Vision analysis preserved (length: {len(retrieved_metadata['vision_analysis'])})")
        else:
            print("❌ Vision analysis LOST during ChromaDB storage")
            
            # Let's check if the vision_analysis field has any issues
            vision_analysis = electrical_segment.get('vision_analysis', '')
            print(f"\nDebugging vision_analysis field:")
            print(f"   - Type: {type(vision_analysis).__name__}")
            print(f"   - Length: {len(vision_analysis)}")
            print(f"   - First 200 chars: {vision_analysis[:200]}")
            
            # Check if there are any problematic characters
            try:
                # Try to encode/decode
                encoded = vision_analysis.encode('utf-8')
                decoded = encoded.decode('utf-8')
                print(f"   - UTF-8 encoding: ✅")
                
                # Try JSON serialization
                json.dumps(vision_analysis)
                print(f"   - JSON serialization: ✅")
                
            except Exception as e:
                print(f"   - Encoding/serialization issue: ❌ ({e})")
        
        # Clean up
        client.delete_collection("test_electrical_plan")
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_electrical_plan_indexing()
