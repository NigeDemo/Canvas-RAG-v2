#!/usr/bin/env python3
"""
Test rebuilding the index and monitor each step to see where vision analysis is lost
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json
from pathlib import Path

def test_index_rebuild():
    """Test rebuilding the index step by step"""
    print("=== TESTING INDEX REBUILD ===\n")
    
    # Check what we have in processed content
    processed_file = Path("data/processed/processed_page_construction_drawing_package_2_metadata.json")
    
    with open(processed_file, 'r', encoding='utf-8') as f:
        content_segments = json.load(f)
    
    print(f"Loaded {len(content_segments)} segments from processed content")
    
    # Count segments with vision analysis
    vision_segments = [s for s in content_segments if 'vision_analysis' in s]
    print(f"Segments with vision analysis: {len(vision_segments)}")
    
    # Find the electrical plan specifically
    electrical_plan = None
    for seg in content_segments:
        if seg.get('alt_text') == '16-1421-312f BG T2 electrical plan_Redacted.jpg':
            electrical_plan = seg
            break
    
    if electrical_plan:
        print(f"✅ Electrical plan found in processed content")
        print(f"   - Has vision_analysis: {'vision_analysis' in electrical_plan}")
        print(f"   - Vision analysis length: {len(electrical_plan.get('vision_analysis', ''))}")
    else:
        print("❌ Electrical plan not found in processed content")
        return
    
    # Now test the IndexBuilder
    print(f"\n=== TESTING INDEX BUILDER ===")
    
    try:
        from indexing.vector_store import IndexBuilder
        from utils.logger import get_logger
        
        # Create a test IndexBuilder
        print("Creating IndexBuilder...")
        index_builder = IndexBuilder()
        
        # Test building index from our processed content
        print("Building index from processed content...")
        
        # Before building, let's manually check what will be passed
        documents = []
        metadata = []
        content_for_embedding = []
        
        for segment in content_segments:
            # Create document text for indexing (same as IndexBuilder)
            doc_text = ""
            if "text" in segment and segment["text"]:
                doc_text = segment["text"]
            elif segment.get("content_type") == "image":
                doc_text = f"[Image: {segment.get('filename', 'image')}]"
                if "alt_text" in segment:
                    doc_text += f" {segment['alt_text']}"
            elif segment.get("content_type") == "image_reference":
                doc_text = f"[Image: {segment.get('alt_text', 'architectural drawing')}]"
                if segment.get("title"):
                    doc_text += f" - {segment['title']}"
            
            if doc_text:
                documents.append(doc_text)
                metadata.append(segment)
                content_for_embedding.append(segment)
        
        print(f"Prepared {len(documents)} documents for indexing")
        
        # Check if electrical plan is in the prepared data
        electrical_in_prepared = None
        for i, seg in enumerate(metadata):
            if seg.get('alt_text') == '16-1421-312f BG T2 electrical plan_Redacted.jpg':
                electrical_in_prepared = seg
                electrical_index = i
                break
        
        if electrical_in_prepared:
            print(f"✅ Electrical plan found in prepared metadata at index {electrical_index}")
            print(f"   - Has vision_analysis: {'vision_analysis' in electrical_in_prepared}")
            print(f"   - Document text: {documents[electrical_index]}")
        else:
            print("❌ Electrical plan not found in prepared metadata")
            return
        
        # Now actually build the index
        print(f"\nBuilding index...")
        index_builder.build_index(processed_file)
        
        print(f"Index built successfully")
        
        # Test retrieval
        print(f"\n=== TESTING RETRIEVAL ===")
        
        retriever = index_builder.get_retriever()
        
        # Try to retrieve the electrical plan
        results = retriever.search("electrical plan", k=5)
        
        print(f"Retrieved {len(results)} results for 'electrical plan'")
        
        # Check if electrical plan is in results
        for i, result in enumerate(results):
            if 'electrical' in result.get('content', '').lower():
                print(f"Found electrical plan result {i}:")
                print(f"   - Content: {result['content'][:100]}...")
                print(f"   - Metadata keys: {sorted(result.get('metadata', {}).keys())}")
                print(f"   - Has vision_analysis: {'vision_analysis' in result.get('metadata', {})}")
                if 'vision_analysis' in result.get('metadata', {}):
                    print(f"   - Vision analysis length: {len(result['metadata']['vision_analysis'])}")
                break
        else:
            print("❌ No electrical plan found in retrieval results")
        
    except Exception as e:
        print(f"❌ IndexBuilder test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_index_rebuild()
