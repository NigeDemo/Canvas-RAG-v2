"""Vector storage and indexing for Canvas RAG system."""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import json
import pickle
from dataclasses import dataclass

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False

from ..config.settings import settings
from ..embeddings.multimodal_embeddings import EmbeddingManager
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SearchResult:
    """Individual search result."""
    id: str
    text: str
    score: float
    rank: int
    metadata: Dict[str, Any]

class VectorStore:
    """ChromaDB-based vector storage."""
    
    def __init__(self, collection_name: str = None, persist_directory: str = None):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory for persistent storage
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is required for vector storage")
        
        self.collection_name = collection_name or settings.chroma_collection_name
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        
        # Ensure directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Canvas RAG multimodal content"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, 
                     documents: List[str], 
                     embeddings: np.ndarray, 
                     metadata: List[Dict[str, Any]],
                     ids: List[str] = None) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document texts
            embeddings: Document embeddings
            metadata: Document metadata
            ids: Document IDs (generated if not provided)
        """
        if len(documents) != len(embeddings) or len(documents) != len(metadata):
            raise ValueError("Documents, embeddings, and metadata must have same length")
        
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Convert numpy array to list for ChromaDB
        embeddings_list = embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
        
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadata
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def search(self, 
               query_embedding: np.ndarray, 
               n_results: int = 10,
               where: Dict[str, Any] = None) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding
            n_results: Number of results to return
            where: Metadata filters
            
        Returns:
            List of search results
        """
        query_embedding_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
        
        results = self.collection.query(
            query_embeddings=[query_embedding_list],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0], 
            results['distances'][0]
        )):
            # Convert distance to similarity score (higher is better)
            score = 1.0 / (1.0 + distance)
            
            result = SearchResult(
                id=results['ids'][0][i],
                text=doc,
                score=score,
                rank=i + 1,
                metadata=metadata
            )
            search_results.append(result)
        
        return search_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"name": self.collection_name, "count": 0}

class SparseIndex:
    """BM25-based sparse index for keyword search."""
    
    def __init__(self):
        """Initialize sparse index."""
        if not BM25_AVAILABLE:
            raise ImportError("rank-bm25 is required for sparse indexing")
        
        self.bm25 = None
        self.documents = []
        self.metadata = []
        self.tokenized_docs = []
    
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Basic tokenization - can be enhanced with domain-specific terms
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]]) -> None:
        """
        Add documents to sparse index.
        
        Args:
            documents: List of document texts
            metadata: Document metadata
        """
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        
        # Tokenize documents
        tokenized = [self.tokenize(doc) for doc in documents]
        self.tokenized_docs.extend(tokenized)
        
        # Rebuild BM25 index
        self.bm25 = BM25Okapi(self.tokenized_docs)
        
        logger.info(f"Added {len(documents)} documents to sparse index")
    
    def search(self, query: str, n_results: int = 10) -> List[SearchResult]:
        """
        Search using BM25.
        
        Args:
            query: Query string
            n_results: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.bm25:
            return []
        
        query_tokens = self.tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top results
        top_indices = np.argsort(scores)[-n_results:][::-1]
        
        search_results = []
        for rank, idx in enumerate(top_indices):
            if scores[idx] > 0:  # Only include positive scores
                result = SearchResult(
                    id=f"sparse_{idx}",
                    text=self.documents[idx],
                    score=scores[idx],
                    rank=rank + 1,
                    metadata=self.metadata[idx]
                )
                search_results.append(result)
        
        return search_results

class HybridRetriever:
    """Combines dense and sparse retrieval with fusion."""
    
    def __init__(self, 
                 vector_store: VectorStore, 
                 sparse_index: SparseIndex,
                 embedding_manager: EmbeddingManager,
                 alpha: float = 0.5):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_store: Dense vector store
            sparse_index: Sparse BM25 index
            embedding_manager: Embedding model manager
            alpha: Fusion weight (0=sparse only, 1=dense only)
        """
        self.vector_store = vector_store
        self.sparse_index = sparse_index
        self.embedding_manager = embedding_manager
        self.alpha = alpha
        
        logger.info(f"Initialized hybrid retriever with alpha={alpha}")
    
    def reciprocal_rank_fusion(self, 
                              dense_results: List[SearchResult],
                              sparse_results: List[SearchResult],
                              k: int = 60) -> List[Tuple[int, float]]:
        """
        Combine results using Reciprocal Rank Fusion.
        
        Args:
            dense_results: Results from dense retrieval
            sparse_results: Results from sparse retrieval
            k: RRF parameter
            
        Returns:
            List of (original_index, fused_score) tuples
        """
        # Create mapping from document to results
        doc_scores = {}
        
        # Add dense results
        for result in dense_results:
            doc_id = result.text  # Use text as identifier
            rrf_score = 1.0 / (k + result.rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + self.alpha * rrf_score
        
        # Add sparse results
        for result in sparse_results:
            doc_id = result.text
            rrf_score = 1.0 / (k + result.rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (1 - self.alpha) * rrf_score
        
        # Sort by fused score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_docs
    
    def retrieve(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval.
        
        Args:
            query: Query string
            n_results: Number of results to return
            
        Returns:
            List of result dictionaries
        """
        try:
            # Dense retrieval
            query_embedding = self.embedding_manager.embed_query(query)
            dense_results = self.vector_store.search(query_embedding, n_results)
            
            # Sparse retrieval
            sparse_results = self.sparse_index.search(query, n_results)
            
            # Fusion
            fused_docs = self.reciprocal_rank_fusion(dense_results, sparse_results)
            
            # Create final results
            final_results = []
            result_map = {}
            
            # Build result mapping
            for result in dense_results + sparse_results:
                result_map[result.text] = result
            
            # Get top fused results
            for i, (doc_text, fused_score) in enumerate(fused_docs[:n_results]):
                if doc_text in result_map:
                    original_result = result_map[doc_text]
                    
                    final_result = {
                        "id": original_result.id,
                        "text": original_result.text,
                        "score": fused_score,
                        "rank": i + 1,
                        "metadata": original_result.metadata,
                        "dense_score": getattr(original_result, 'dense_score', 0),
                        "sparse_score": getattr(original_result, 'sparse_score', 0)
                    }
                    final_results.append(final_result)
            
            logger.info(f"Retrieved {len(final_results)} results for query: {query[:50]}...")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {e}")
            return []

class IndexBuilder:
    """Builds and manages indexes for the RAG system."""
    
    def __init__(self, embedding_model_type: str = "openai"):
        """
        Initialize index builder.
        
        Args:
            embedding_model_type: Type of embedding model to use
        """
        self.embedding_manager = EmbeddingManager(model_type=embedding_model_type)
        self.vector_store = VectorStore()
        self.sparse_index = SparseIndex()
        
        logger.info(f"Initialized index builder with {embedding_model_type} embeddings")
    
    def build_index(self, processed_content_path: Path) -> None:
        """
        Build complete index from processed content.
        
        Args:
            processed_content_path: Path to processed content JSON file
        """
        logger.info(f"Building index from: {processed_content_path}")
        
        # Load processed content
        with open(processed_content_path, 'r', encoding='utf-8') as f:
            content_segments = json.load(f)
        
        # Prepare data
        documents = []
        metadata = []
        content_for_embedding = []
        
        for segment in content_segments:
            # Extract document text
            doc_text = ""
            if "text" in segment and segment["text"]:
                doc_text = segment["text"]
            elif segment.get("content_type") == "image_reference":
                doc_text = f"[Image: {segment.get('alt_text', 'architectural drawing')}]"
            
            if doc_text:
                documents.append(doc_text)
                metadata.append(segment)
                content_for_embedding.append(segment)
        
        logger.info(f"Preparing to index {len(documents)} documents")
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedding_manager.embed_content(content_for_embedding)
        
        # Add to vector store
        logger.info("Building dense index...")
        self.vector_store.add_documents(documents, embeddings, metadata)
        
        # Add to sparse index
        logger.info("Building sparse index...")
        self.sparse_index.add_documents(documents, metadata)
        
        logger.info("Index building complete!")
    
    def get_retriever(self) -> HybridRetriever:
        """Get hybrid retriever instance."""
        return HybridRetriever(
            self.vector_store,
            self.sparse_index, 
            self.embedding_manager,
            alpha=settings.hybrid_fusion_alpha
        )

__all__ = ["VectorStore", "SparseIndex", "HybridRetriever", "IndexBuilder", "SearchResult"]
