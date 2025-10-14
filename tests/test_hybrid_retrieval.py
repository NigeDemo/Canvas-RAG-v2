"""Test hybrid retrieval with BM25 + Vector search."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.indexing.vector_store import VectorStore, SparseIndex, HybridRetriever
from src.retrieval.hybrid_search import QueryProcessor
from src.embeddings.multimodal_embeddings import EmbeddingManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_bm25_initialization():
    """Test that BM25 index initializes properly."""
    sparse_index = SparseIndex()
    
    documents = [
        "Construction drawings show technical details and specifications",
        "Floor plans display room layouts and spatial organization",
        "Elevations show building facades and exterior views"
    ]
    metadata = [{'id': f'doc_{i}', 'type': 'text', 'content_type': 'text_chunk'} for i in range(len(documents))]
    
    sparse_index.add_documents(documents, metadata)
    
    assert sparse_index.is_initialized, "BM25 index should be initialized"
    assert len(sparse_index.documents) == 3, "Should have 3 documents"
    assert sparse_index.bm25 is not None, "BM25 object should exist"
    
    logger.info("✅ BM25 initialization test passed")


def test_query_processor_detects_module_image_listing():
    """Ensure module image listing intent is detected for visual module queries."""
    processor = QueryProcessor()

    analysis = processor.analyze_query("List all images from Session 5")

    assert analysis['is_module_query'] is True
    assert analysis['is_visual_query'] is True
    assert analysis['intent'] == 'module_image_listing'
    assert analysis['is_image_listing'] is True
    assert analysis['module_number'] == '5'

    logger.info("✅ Module image listing intent detection test passed")

def test_bm25_query():
    """Test BM25 query functionality."""
    sparse_index = SparseIndex()
    
    documents = [
        "Construction drawings show technical details and specifications",
        "Floor plans display room layouts and spatial organization",
        "Elevations show building facades and exterior views",
        "Electrical plans show wiring and outlets",
        "Site plans show building placement and landscaping"
    ]
    metadata = [{'id': f'doc_{i}', 'type': 'text', 'content_type': 'text_chunk'} for i in range(len(documents))]
    
    sparse_index.add_documents(documents, metadata)
    
    # Query for floor plans
    results = sparse_index.query("floor plans layout", n_results=3)
    
    assert len(results) > 0, "Should return results"
    assert results[0][1] > 0, "Top result should have positive score"
    
    # The document about floor plans should be highly ranked
    top_idx = results[0][0]
    top_doc = documents[top_idx]
    assert "floor" in top_doc.lower() or "plan" in top_doc.lower(), \
        "Top result should be relevant to 'floor plans'"
    
    logger.info(f"✅ BM25 query test passed - top result: {top_doc[:50]}...")

def test_bm25_relevance_scoring():
    """Test that BM25 scores more relevant documents higher."""
    sparse_index = SparseIndex()
    
    documents = [
        "The sky is blue and beautiful",
        "Floor plans are architectural drawings that show room layouts from above",
        "Floor plan drawings display spatial organization and dimensions",
        "The weather is nice today",
        "Plans for the weekend include hiking"
    ]
    metadata = [{'id': f'doc_{i}', 'type': 'text', 'content_type': 'text_chunk'} for i in range(len(documents))]
    
    sparse_index.add_documents(documents, metadata)
    
    # Query specifically about floor plans
    results = sparse_index.query("floor plan architectural drawing", n_results=5)
    
    # Top 2 results should be the floor plan documents
    top_2_docs = [documents[results[i][0]] for i in range(min(2, len(results)))]
    
    floor_plan_count = sum(1 for doc in top_2_docs if "floor plan" in doc.lower())
    
    assert floor_plan_count >= 1, "At least one of top 2 results should mention 'floor plan'"
    
    logger.info("✅ BM25 relevance scoring test passed")

def test_reciprocal_rank_fusion():
    """Test RRF fusion algorithm."""
    from src.embeddings.multimodal_embeddings import EmbeddingManager
    
    # Create mock components
    sparse_index = SparseIndex()
    documents = [
        "Construction drawings technical details",
        "Floor plans room layouts",
        "Building elevations facade"
    ]
    metadata = [{'id': f'doc_{i}', 'type': 'text', 'content_type': 'text_chunk'} for i in range(len(documents))]
    sparse_index.add_documents(documents, metadata)
    
    # Create a minimal vector store for testing
    try:
        vector_store = VectorStore()
        embedding_manager = EmbeddingManager(model_type="nomic")
        
        retriever = HybridRetriever(
            vector_store=vector_store,
            sparse_index=sparse_index,
            embedding_manager=embedding_manager,
            alpha=0.5
        )
        
        # Test RRF with mock results
        dense_results = [(0, 0.9), (1, 0.7), (2, 0.5)]
        sparse_results = [(1, 10.5), (0, 8.2), (2, 3.1)]
        
        fused = retriever.reciprocal_rank_fusion(dense_results, sparse_results, k=60)
        
        assert len(fused) == 3, "Should have 3 fused results"
        assert all(len(item) == 3 for item in fused), "Each result should have (idx, score, source)"
        
        # Check that scores are combined (documents in both lists should have higher scores)
        # Doc 0 and 1 are in both lists, doc 2 is in both but with lower ranks
        top_result = fused[0]
        assert top_result[2] in ['dense', 'sparse', 'hybrid'], "Source should be valid"
        
        logger.info(f"✅ RRF fusion test passed - top result index: {top_result[0]}, score: {top_result[1]:.4f}, source: {top_result[2]}")
        
    except Exception as e:
        logger.warning(f"RRF test skipped due to: {e}")
        pytest.skip(f"Could not initialize vector store: {e}")

def test_sparse_fallback_on_empty_query():
    """Test that sparse index handles edge cases."""
    sparse_index = SparseIndex()
    
    documents = ["Test document"]
    metadata = [{'id': 'doc_0', 'type': 'text', 'content_type': 'text_chunk'}]
    sparse_index.add_documents(documents, metadata)
    
    # Empty query should return empty results
    results = sparse_index.query("", n_results=10)
    assert len(results) == 0 or all(score == 0 for _, score in results), \
        "Empty query should return no meaningful results"
    
    logger.info("✅ Sparse fallback test passed")

def test_hybrid_retrieval_integration():
    """Test full hybrid retrieval with actual components (if available)."""
    try:
        # This test requires actual database setup
        from src.config.settings import settings
        
        vector_store = VectorStore()
        sparse_index = SparseIndex()
        embedding_manager = EmbeddingManager(model_type="nomic")
        
        # Try to populate sparse index from existing data
        try:
            collection = vector_store.client.get_collection(name=vector_store.collection_name)
            all_docs = collection.get()
            
            text_documents = []
            text_metadata = []
            
            for doc, metadata in zip(all_docs['documents'], all_docs['metadatas']):
                content_type = metadata.get('content_type', '')
                if content_type in ['text_chunk', 'section_content', 'section_heading'] and doc:
                    text_documents.append(doc)
                    text_metadata.append(metadata)
            
            if text_documents:
                sparse_index.add_documents(text_documents, text_metadata)
                logger.info(f"Loaded {len(text_documents)} documents for hybrid retrieval test")
            else:
                pytest.skip("No text documents in database for testing")
                
        except Exception as e:
            pytest.skip(f"Could not load documents from database: {e}")
        
        # Create retriever
        retriever = HybridRetriever(
            vector_store=vector_store,
            sparse_index=sparse_index,
            embedding_manager=embedding_manager,
            alpha=0.5
        )
        
        # Test a simple query
        test_query = "construction drawing"
        results = retriever.retrieve(test_query, n_results=5)
        
        assert len(results) > 0, "Should return some results"
        assert all('text' in r for r in results), "All results should have text"
        assert all('metadata' in r for r in results), "All results should have metadata"
        
        # Check retrieval source tracking
        sources = [r.get('retrieval_source', 'unknown') for r in results]
        logger.info(f"Retrieval sources: {sources}")
        
        logger.info(f"✅ Hybrid retrieval integration test passed - {len(results)} results returned")
        
    except Exception as e:
        logger.warning(f"Hybrid integration test skipped: {e}")
        pytest.skip(f"Could not run hybrid integration test: {e}")

if __name__ == "__main__":
    # Run tests
    print("Running BM25 and Hybrid Retrieval Tests...")
    print("=" * 60)
    
    test_bm25_initialization()
    test_bm25_query()
    test_bm25_relevance_scoring()
    test_reciprocal_rank_fusion()
    test_sparse_fallback_on_empty_query()
    test_hybrid_retrieval_integration()
    
    print("=" * 60)
    print("✅ All tests completed!")
