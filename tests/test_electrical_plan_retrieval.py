#!/usr/bin/env python3
"""Test the electrical plan query with the new image-first retrieval."""

from src.indexing.vector_store import IndexBuilder
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_electrical_plan_query():
    """Test electrical plan query with new image-first retrieval."""
    
    # Initialize system
    index_builder = IndexBuilder(embedding_model_type="openai")
    retriever = index_builder.get_retriever()
    
    # Test the electrical plan query
    query = "Can you describe the electrical plan"
    logger.info(f"Testing query: {query}")
    
    results = retriever.retrieve(query, n_results=10)
    
    print(f"\n=== Electrical Plan Query Results ===")
    print(f"Total results: {len(results)}")
    
    image_count = 0
    text_count = 0
    
    for i, result in enumerate(results):
        metadata = result["metadata"]
        content_type = metadata.get("content_type", "")
        file_name = metadata.get("file_name", "unknown")
        alt_text = metadata.get("alt_text", "")
        has_vision = metadata.get("has_vision_analysis", False)
        
        is_image = (content_type == "image" or has_vision)
        
        if is_image:
            image_count += 1
            display_name = alt_text if alt_text else file_name
            print(f"  {i+1}. IMAGE: {display_name}")
            print(f"     Vision analysis: {has_vision}")
            print(f"     Score: {result['score']:.3f}")
            
            # Check if this might be electrical plan
            if "electrical" in display_name.lower() or "elec" in display_name.lower():
                print(f"     *** POTENTIAL ELECTRICAL PLAN ***")
                
                # Show vision analysis if available
                if has_vision and "vision_analysis" in metadata:
                    analysis = metadata["vision_analysis"][:200] + "..."
                    print(f"     Vision analysis preview: {analysis}")
        else:
            text_count += 1
            print(f"  {i+1}. TEXT: {file_name}")
    
    print(f"\nSummary: {text_count} text, {image_count} images")
    
    # Check if we have the electrical plan specifically
    electrical_images = [r for r in results if "electrical" in r["metadata"].get("alt_text", "").lower()]
    if electrical_images:
        print(f"\n✅ Found {len(electrical_images)} electrical plan images!")
        for img in electrical_images:
            print(f"   - {img['metadata'].get('alt_text', 'unknown')}")
    else:
        print(f"\n❌ No electrical plan images found in results")
    
    return results

if __name__ == "__main__":
    test_electrical_plan_query()
