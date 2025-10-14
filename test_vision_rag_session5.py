"""Test script to diagnose Session 5 query issue in vision_chat_app.py"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.config.settings import settings
from src.indexing.vector_store import IndexBuilder
from src.retrieval.hybrid_search import HybridSearchEngine
from src.vision.vision_rag_integration import create_vision_rag_system

def test_session5_query():
    """Test the Session 5 query end-to-end."""
    
    print("=" * 80)
    print("TESTING SESSION 5 QUERY IN VISION RAG SYSTEM")
    print("=" * 80)
    
    # Initialize system (same as vision_chat_app does)
    print("\n1. Initializing system...")
    index_builder = IndexBuilder(embedding_model_type="openai")
    retriever = index_builder.get_retriever()
    search_engine = HybridSearchEngine(retriever)
    
    print(f"✅ Search engine initialized")
    print(f"   - Retriever: {type(retriever).__name__}")
    print(f"   - Search engine: {type(search_engine).__name__}")
    
    # Create vision RAG system
    print("\n2. Creating Vision RAG system...")
    vision_rag = create_vision_rag_system(search_engine)
    
    print(f"✅ Vision RAG system created")
    print(f"   - Type: {type(vision_rag).__name__}")
    print(f"   - Has search engine: {vision_rag.search_engine is not None}")
    
    # Test query
    query = "What is covered in Session 5?"
    
    print(f"\n3. Testing query: '{query}'")
    print("-" * 80)
    
    # First, test search engine directly
    print("\n3a. Testing search_engine.search() directly...")
    search_results = search_engine.search(query, n_results=10)
    
    print(f"\nSearch Results:")
    print(f"   - Total results: {search_results.get('total_results', 0)}")
    print(f"   - Query analysis:")
    analysis = search_results.get('query_analysis', {})
    print(f"      - Is module query: {analysis.get('is_module_query', False)}")
    print(f"      - Module number: {analysis.get('module_number', 'N/A')}")
    print(f"      - Intent: {analysis.get('intent', 'N/A')}")
    
    if search_results.get('enhanced_query'):
        print(f"   - Enhanced query: '{search_results['enhanced_query']}'")
    
    # Show first few results
    print(f"\nFirst 3 results:")
    for i, result in enumerate(search_results.get('results', [])[:3], 1):
        metadata = result.metadata if hasattr(result, 'metadata') else result.get('metadata', {})
        text = result.text if hasattr(result, 'text') else result.get('text', '')
        
        print(f"\n   Result {i}:")
        print(f"      Parent Module: {metadata.get('parent_module', 'N/A')}")
        print(f"      Content Type: {metadata.get('content_type', 'N/A')}")
        print(f"      Source: {metadata.get('source', 'N/A')}")
        print(f"      Text preview: {text[:150]}...")
    
    # Now test vision_rag.query()
    print("\n\n3b. Testing vision_rag.query()...")
    result = vision_rag.query(query, enable_vision=False, max_images=0)
    
    print(f"\nVision RAG Result:")
    print(f"   - Success: {result.success}")
    print(f"   - Query type: {result.query_type}")
    print(f"   - Processing time: {result.processing_time:.2f}s")
    print(f"   - Text context length: {len(result.text_context)} chars")
    print(f"   - Image references: {len(result.image_references)}")
    
    print(f"\n   Response:")
    print(f"   {'-' * 76}")
    # Print response with proper line wrapping
    response_lines = result.response.split('\n')
    for line in response_lines[:10]:  # First 10 lines
        print(f"   {line}")
    if len(response_lines) > 10:
        print(f"   ... ({len(response_lines) - 10} more lines)")
    print(f"   {'-' * 76}")
    
    # Check if response contains actual content
    print(f"\n4. Response Analysis:")
    generic_phrases = [
        "likely covers",
        "probably discusses",
        "might include",
        "specific details are not provided",
        "curriculum likely covers"
    ]
    
    is_generic = any(phrase in result.response.lower() for phrase in generic_phrases)
    print(f"   - Contains generic phrases: {is_generic}")
    
    if is_generic:
        print(f"   ⚠️  PROBLEM DETECTED: Response appears to be generic/hallucinated")
        print(f"   - Not using actual indexed content from Session 5 files")
    
    # Check if Canvas module info is in text context
    has_module_info = 'Session 5' in result.text_context or 'Steel Frame' in result.text_context
    print(f"   - Text context contains Session 5 content: {has_module_info}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS COMPLETE")
    print("=" * 80)
    
    if analysis.get('is_module_query'):
        print("\n✅ Module query detection: WORKING")
    else:
        print("\n❌ Module query detection: FAILED")
    
    if search_results.get('total_results', 0) > 0:
        print("✅ Retrieval: WORKING")
    else:
        print("❌ Retrieval: FAILED")
    
    if has_module_info:
        print("✅ Context extraction: WORKING")
    else:
        print("❌ Context extraction: FAILED")
    
    if not is_generic:
        print("✅ Response generation: WORKING")
    else:
        print("❌ Response generation: GENERIC (not using context properly)")
        print("\nPOSSIBLE CAUSES:")
        print("1. VisionEnhancedResponseGenerator not using 'module_content' template")
        print("2. Text context not being formatted properly for LLM")
        print("3. LLM not seeing Canvas module structure explanation")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_session5_query()
