"""Vector database and indexing functionality."""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from rank_bm25 import BM25Okapi

from ..config.settings import settings
from ..embeddings.multimodal_embeddings import EmbeddingManager
from ..utils.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""
    
    def __init__(self, persist_directory: str = None, collection_name: str = None):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is required for vector storage")
        
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        self.collection_name = collection_name or settings.chroma_collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Canvas RAG multimodal content"}
        )
        
        logger.info(f"Initialized vector store with collection: {self.collection_name}")
    
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
            metadata: List of metadata dictionaries
            ids: Optional list of document IDs
        """
        try:
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Convert numpy array to list for ChromaDB
            embeddings_list = embeddings.tolist()
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings_list,
                metadatas=metadata,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def query(self, 
              query_embedding: np.ndarray, 
              n_results: int = 10, 
              where: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Query the vector store.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Query results dictionary
        """
        try:
            # Convert numpy array to list
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return {"documents": [], "metadatas": [], "distances": [], "ids": []}
    
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
            return {}

class SparseIndex:
    """Manages sparse (keyword) indexing using BM25."""
    
    def __init__(self):
        """Initialize sparse index."""
        self.bm25 = None
        self.documents = []
        self.metadata = []
        self.tokenized_docs = []
        
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]]) -> None:
        """
        Add documents to the sparse index.
        
        Args:
            documents: List of document texts
            metadata: List of metadata dictionaries
        """
        try:
            self.documents.extend(documents)
            self.metadata.extend(metadata)
            
            # Simple tokenization (can be improved with proper preprocessing)
            new_tokenized = [doc.lower().split() for doc in documents]
            self.tokenized_docs.extend(new_tokenized)
            
            # Rebuild BM25 index
            self.bm25 = BM25Okapi(self.tokenized_docs)
            
            logger.info(f"Added {len(documents)} documents to sparse index")
            
        except Exception as e:
            logger.error(f"Error adding documents to sparse index: {e}")
            raise
    
    def query(self, query: str, n_results: int = 10) -> List[Tuple[int, float]]:
        """
        Query the sparse index.
        
        Args:
            query: Query string
            n_results: Number of results to return
            
        Returns:
            List of (document_index, score) tuples
        """
        try:
            if self.bm25 is None:
                logger.warning("BM25 index not initialized")
                return []
            
            tokenized_query = query.lower().split()
            scores = self.bm25.get_scores(tokenized_query)
            
            # Get top results
            top_indices = np.argsort(scores)[::-1][:n_results]
            results = [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying sparse index: {e}")
            return []

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
            vector_store: Vector store instance
            sparse_index: Sparse index instance
            embedding_manager: Embedding manager instance
            alpha: Fusion weight (0.0 = only sparse, 1.0 = only dense)
        """
        self.vector_store = vector_store
        self.sparse_index = sparse_index
        self.embedding_manager = embedding_manager
        self.alpha = alpha
        
        logger.info(f"Initialized hybrid retriever with alpha={alpha}")
    
    def reciprocal_rank_fusion(self, 
                              dense_results: List[Tuple[int, float]], 
                              sparse_results: List[Tuple[int, float]], 
                              k: int = 60) -> List[Tuple[int, float]]:
        """
        Combine dense and sparse results using Reciprocal Rank Fusion.
        
        Args:
            dense_results: List of (index, score) from dense retrieval
            sparse_results: List of (index, score) from sparse retrieval
            k: RRF constant
            
        Returns:
            Fused results as list of (index, score) tuples
        """
        # Create score dictionaries
        dense_scores = {idx: 1.0 / (rank + k) for rank, (idx, _) in enumerate(dense_results)}
        sparse_scores = {idx: 1.0 / (rank + k) for rank, (idx, _) in enumerate(sparse_results)}
        
        # Get all unique indices
        all_indices = set(dense_scores.keys()) | set(sparse_scores.keys())
        
        # Calculate fused scores
        fused_scores = []
        for idx in all_indices:
            dense_score = dense_scores.get(idx, 0.0)
            sparse_score = sparse_scores.get(idx, 0.0)
            
            # Weighted combination
            fused_score = self.alpha * dense_score + (1 - self.alpha) * sparse_score
            fused_scores.append((idx, fused_score))
        
        # Sort by fused score
        fused_scores.sort(key=lambda x: x[1], reverse=True)
        return fused_scores
    
    def retrieve(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval.
        
        Args:
            query: Query string
            n_results: Number of results to return
            
        Returns:
            List of retrieved document dictionaries
        """
        try:
            # Dense retrieval
            query_embedding = self.embedding_manager.embed_query(query)
            dense_vector_results = self.vector_store.query(query_embedding, n_results * 2)
            
            # Convert ChromaDB results to (index, distance) format
            dense_results = []
            if dense_vector_results.get("ids") and dense_vector_results["ids"][0]:
                for i, (doc_id, distance) in enumerate(zip(
                    dense_vector_results["ids"][0], 
                    dense_vector_results["distances"][0]
                )):
                    # Convert distance to similarity score (assuming cosine distance)
                    similarity = 1.0 - distance
                    dense_results.append((i, similarity))
            
            # Sparse retrieval
            sparse_results = self.sparse_index.query(query, n_results * 2)
            
            # Fusion
            if dense_results and sparse_results:
                fused_results = self.reciprocal_rank_fusion(dense_results, sparse_results)
            elif dense_results:
                fused_results = dense_results
            elif sparse_results:
                fused_results = sparse_results
            else:
                logger.warning("No results from either dense or sparse retrieval")
                return []
            
            # Prepare final results
            final_results = []
            for rank, (result_idx, score) in enumerate(fused_results[:n_results]):
                # Get document data
                if result_idx < len(dense_vector_results.get("documents", [[]])[0]):
                    # From dense results
                    doc_text = dense_vector_results["documents"][0][result_idx]
                    metadata = dense_vector_results["metadatas"][0][result_idx]
                    doc_id = dense_vector_results["ids"][0][result_idx]
                elif result_idx < len(self.sparse_index.documents):
                    # From sparse results
                    doc_text = self.sparse_index.documents[result_idx]
                    metadata = self.sparse_index.metadata[result_idx]
                    doc_id = f"sparse_{result_idx}"
                else:
                    continue
                
                result_dict = {
                    "id": doc_id,
                    "text": doc_text,
                    "score": score,
                    "rank": rank + 1,
                    "metadata": metadata
                }
                final_results.append(result_dict)
            
            logger.info(f"Retrieved {len(final_results)} results for query")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {e}")
            return []

class IndexBuilder:
    """Builds and manages the complete indexing system."""
    
    def __init__(self, embedding_model_type: str = "nomic"):
        """
        Initialize index builder.
        
        Args:
            embedding_model_type: Type of embedding model to use
        """
        self.vector_store = VectorStore()
        self.sparse_index = SparseIndex()
        self.embedding_manager = EmbeddingManager(model_type=embedding_model_type)
        
        self.retriever = HybridRetriever(
            self.vector_store,
            self.sparse_index,
            self.embedding_manager,
            alpha=settings.hybrid_fusion_alpha
        )
        
        logger.info("Initialized index builder")
    
    def build_index(self, processed_content_path: Path) -> None:
        """
        Build the complete index from processed content.
        
        Args:
            processed_content_path: Path to processed content JSON file
        """
        logger.info(f"Building index from: {processed_content_path}")
        
        with open(processed_content_path, 'r', encoding='utf-8') as f:
            content_segments = json.load(f)
        
        # Prepare data for indexing
        documents = []
        metadata = []
        content_for_embedding = []
        
        for segment in content_segments:
            # Create document text for indexing
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
        
        if not documents:
            logger.warning("No documents to index")
            return
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedding_manager.embed_content(content_for_embedding)
        
        # Add to vector store
        logger.info("Adding documents to vector store...")
        self.vector_store.add_documents(documents, embeddings, metadata)
        
        # Add to sparse index
        logger.info("Adding documents to sparse index...")
        self.sparse_index.add_documents(documents, metadata)
        
        logger.info(f"Index building complete. Indexed {len(documents)} documents")
    
    def get_retriever(self) -> HybridRetriever:
        """Get the hybrid retriever instance."""
        return self.retriever
