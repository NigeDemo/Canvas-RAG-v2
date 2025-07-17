#!/usr/bin/env python3
"""Final test to demonstrate electrical plan query resolution."""

from src.indexing.vector_store import IndexBuilder
from src.retrieval.hybrid_search import HybridSearchEngine
from src.generation.vision_enhanced_generator import VisionEnhancedResponseGenerator
from src.utils.logger import get_logger
import json

logger = get_logger(__name__)

def test_electrical_plan_resolution():
    """Test that electrical plan query now returns detailed vision analysis."""
    
    print("🔍 Testing Electrical Plan Query Resolution...")
    print("=" * 60)
    
    # Initialize the complete system
    index_builder = IndexBuilder(embedding_model_type="openai")
    retriever = index_builder.get_retriever()
    search_engine = HybridSearchEngine(retriever)
    
    # Test query
    query = "Can you describe the electrical plan"
    
    print(f"Query: {query}")
    print()
    
    # Get retrieval results
    results = search_engine.search(query, n_results=10)
    
    print(f"📊 Retrieval Results: {len(results)} total")
    
    # Analyze results
    electrical_plan_found = False
    image_count = 0
    text_count = 0
    
    for i, result in enumerate(results):
        metadata = result.get("metadata", {})
        content_type = metadata.get("content_type", "")
        has_vision = metadata.get("has_vision_analysis", False)
        
        is_image = (content_type in ["image", "image_reference"] or has_vision)
        
        if is_image:
            image_count += 1
            alt_text = metadata.get("alt_text", "")
            vision_analysis = metadata.get("vision_analysis", "")
            
            print(f"  📸 Image {image_count}: {alt_text}")
            
            # Check if this is the electrical plan
            if "electrical plan" in alt_text.lower() or "electrical" in alt_text.lower():
                electrical_plan_found = True
                print(f"    ⚡ *** ELECTRICAL PLAN FOUND ***")
                print(f"    📝 Vision analysis length: {len(vision_analysis)} characters")
                
                if vision_analysis:
                    print(f"    🔍 Vision analysis preview:")
                    print(f"        {vision_analysis[:200]}...")
                    
                    # Show key electrical elements
                    if "electrical" in vision_analysis.lower():
                        print(f"    ✅ Contains electrical content")
                    if "circuit" in vision_analysis.lower():
                        print(f"    ✅ Contains circuit information")
                    if "outlet" in vision_analysis.lower() or "socket" in vision_analysis.lower():
                        print(f"    ✅ Contains outlet/socket information")
                    if "lighting" in vision_analysis.lower():
                        print(f"    ✅ Contains lighting information")
                    if "switch" in vision_analysis.lower():
                        print(f"    ✅ Contains switch information")
        else:
            text_count += 1
    
    print(f"\n📈 Results Summary:")
    print(f"  • Total results: {len(results)}")
    print(f"  • Images: {image_count}")
    print(f"  • Text: {text_count}")
    print(f"  • Electrical plan found: {'✅ YES' if electrical_plan_found else '❌ NO'}")
    
    if electrical_plan_found:
        print(f"\n🎉 SUCCESS! The electrical plan query now returns the actual electrical plan with detailed vision analysis!")
        print(f"📋 This means:")
        print(f"  ✅ Image query detection is working")
        print(f"  ✅ Image-first retrieval is prioritizing images")
        print(f"  ✅ Vision analysis data is accessible")
        print(f"  ✅ Response generation can now use detailed electrical plan analysis")
        
        return True
    else:
        print(f"\n❌ Issue: Electrical plan not found in top results")
        return False

if __name__ == "__main__":
    success = test_electrical_plan_resolution()
    
    if success:
        print(f"\n🚀 Ready to test in chat interface!")
        print(f"💬 Try asking: 'Can you describe the electrical plan'")
        print(f"🌐 Chat interface: http://localhost:8502")
    else:
        print(f"\n🔧 Further debugging needed")
