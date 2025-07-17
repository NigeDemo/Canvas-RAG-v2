"""Vector database and indexing functionality."""

import json
import uuid
import re
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
    """BM25-based sparse index for text retrieval."""
    
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.bm25 = None
        self.is_initialized = False
        
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]]):
        """Add documents to the sparse index."""
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        
        # Tokenize documents for BM25
        tokenized_docs = [doc.lower().split() for doc in self.documents]
        
        if tokenized_docs:
            self.bm25 = BM25Okapi(tokenized_docs)
            self.is_initialized = True
            logger.info(f"Sparse index built with {len(self.documents)} documents")
        else:
            logger.warning("No documents to build sparse index")
    
    def query(self, query: str, n_results: int = 10) -> List[Tuple[int, float]]:
        """Query the sparse index."""
        if not self.is_initialized:
            logger.warning("Sparse index not initialized")
            return []
            
        try:
            tokenized_query = query.lower().split()
            scores = self.bm25.get_scores(tokenized_query)
            
            # Get top results with their indices
            results = [(i, score) for i, score in enumerate(scores)]
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results[:n_results]
            
        except Exception as e:
            logger.error(f"Error querying sparse index: {e}")
            return []

class HybridRetriever:
    """Hybrid retrieval combining dense and sparse search with image boosting."""
    
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
        
        # Image-related query keywords for boosting
        self.image_keywords = [
            'image', 'picture', 'photo', 'drawing', 'diagram', 'plan', 'elevation', 
            'section', 'detail', 'sketch', 'illustration', 'figure', 'visual', 
            'electrical plan', 'floor plan', 'site plan', 'construction drawing',
            'architectural drawing', 'blueprint', 'schematic', 'layout', 'design',
            'show me', 'what does', 'look like', 'appear', 'visible', 'see',
            'describe', 'analysis', 'analyze', 'examine', 'identify'
        ]
        
        logger.info(f"Initialized hybrid retriever with alpha={alpha}")
    
    def is_image_query(self, query: str) -> bool:
        """Detect if query is requesting image/visual content."""
        query_lower = query.lower()
        
        # Check for image-related keywords
        for keyword in self.image_keywords:
            if keyword in query_lower:
                return True
                
        # Check for visual analysis patterns
        visual_patterns = [
            r'\b(what|how|where|which).*(show|display|appear|look|visible)',
            r'\b(describe|analyze|examine|identify).*(image|drawing|plan|diagram)',
            r'\b(electrical|floor|site|construction).*(plan|drawing|diagram)',
            r'\bcan you (see|find|identify|describe)',
            r'\bshow me.*'
        ]
        
        for pattern in visual_patterns:
            if re.search(pattern, query_lower):
                return True
                
        return False
    
    def boost_image_results(self, results: List[Tuple[int, float]], query: str, 
                          dense_vector_results: Dict[str, Any], 
                          boost_factor: float = 2.0) -> List[Tuple[int, float]]:
        """Boost image results for image-related queries."""
        if not self.is_image_query(query):
            return results
            
        logger.info(f"Detected image query, boosting image results by factor {boost_factor}")
        
        boosted_results = []
        for idx, score in results:
            # Check if this result corresponds to an image
            is_image = False
            try:
                # Check if we have metadata for this result index
                if (dense_vector_results.get("metadatas") and 
                    dense_vector_results["metadatas"][0] and
                    idx < len(dense_vector_results["metadatas"][0])):
                    
                    metadata = dense_vector_results["metadatas"][0][idx]
                    content_type = metadata.get("content_type", "")
                    file_type = metadata.get("file_type", "")
                    
                    # Check if this is an image-based content
                    is_image = (content_type == "image" or 
                              file_type in ["png", "jpg", "jpeg", "pdf"] or
                              metadata.get("has_vision_analysis", False))
                    
                    if is_image:
                        logger.debug(f"Boosting image result {idx} with metadata: {metadata.get('file_name', 'unknown')}")
                        
            except Exception as e:
                logger.warning(f"Error checking image status for result {idx}: {e}")
            
            # Apply boost to image results
            if is_image:
                boosted_score = score * boost_factor
                boosted_results.append((idx, boosted_score))
                logger.debug(f"Boosted image result {idx}: {score:.3f} -> {boosted_score:.3f}")
            else:
                boosted_results.append((idx, score))
        
        # Re-sort by boosted scores
        boosted_results.sort(key=lambda x: x[1], reverse=True)
        
        # Log the effect of boosting
        image_count = sum(1 for idx, score in boosted_results[:10] 
                         if self._is_result_image_from_metadata(idx, dense_vector_results))
        logger.info(f"After boosting, top 10 results contain {image_count} images")
        
        return boosted_results
    
    def _is_result_image_from_metadata(self, idx: int, dense_vector_results: Dict[str, Any]) -> bool:
        """Helper to check if a result index corresponds to an image using metadata."""
        try:
            if (dense_vector_results.get("metadatas") and 
                dense_vector_results["metadatas"][0] and
                idx < len(dense_vector_results["metadatas"][0])):
                
                metadata = dense_vector_results["metadatas"][0][idx]
                content_type = metadata.get("content_type", "")
                file_type = metadata.get("file_type", "")
                
                return (content_type == "image" or 
                       file_type in ["png", "jpg", "jpeg", "pdf"] or
                       metadata.get("has_vision_analysis", False))
        except:
            pass
        return False
    
    def reciprocal_rank_fusion(self, dense_results: List[Tuple[int, float]], 
                              sparse_results: List[Tuple[int, float]], 
                              k: int = 60) -> List[Tuple[int, float]]:
        """Combine dense and sparse results using reciprocal rank fusion."""
        # Calculate RRF scores
        fused_scores = []
        all_indices = set([idx for idx, _ in dense_results] + [idx for idx, _ in sparse_results])
        
        for idx in all_indices:
            # Get ranks (1-indexed)
            dense_rank = next((i + 1 for i, (doc_idx, _) in enumerate(dense_results) if doc_idx == idx), float('inf'))
            sparse_rank = next((i + 1 for i, (doc_idx, _) in enumerate(sparse_results) if doc_idx == idx), float('inf'))
            
            # Calculate RRF score
            dense_score = 1.0 / (k + dense_rank) if dense_rank != float('inf') else 0.0
            sparse_score = 1.0 / (k + sparse_rank) if sparse_rank != float('inf') else 0.0
            
            # Weighted combination
            fused_score = self.alpha * dense_score + (1 - self.alpha) * sparse_score
            fused_scores.append((idx, fused_score))
        
        # Sort by fused score
        fused_scores.sort(key=lambda x: x[1], reverse=True)
        return fused_scores
    
    def retrieve(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval with image boosting.
        
        Args:
            query: Query string
            n_results: Number of results to return
            
        Returns:
            List of retrieved document dictionaries
        """
        try:
            # Check if this is an image query
            is_image_query = self.is_image_query(query)
            
            # For image queries, use a two-stage approach:
            # 1. First get image results using the actual query
            # 2. Then get mixed results and boost images
            if is_image_query:
                logger.info(f"Image query detected, using hybrid image-first retrieval")
                
                # Stage 1: Get image results using the actual query (not just "image")
                image_results = self.vector_store.query(
                    self.embedding_manager.embed_query(query), 
                    n_results=n_results * 2,
                    where={"$or": [
                        {"content_type": {"$eq": "image"}},
                        {"content_type": {"$eq": "image_reference"}},
                        {"has_vision_analysis": {"$eq": True}}
                    ]}
                )
                
                # Stage 2: Get regular results
                query_embedding = self.embedding_manager.embed_query(query)
                dense_vector_results = self.vector_store.query(query_embedding, n_results * 2)
                
                # Combine results, prioritizing relevant images
                final_results = []
                
                # Add relevant image results first
                if image_results.get("ids") and image_results["ids"][0]:
                    for i in range(min(n_results // 2, len(image_results["ids"][0]))):
                        doc_text = image_results["documents"][0][i]
                        metadata = image_results["metadatas"][0][i]
                        doc_id = image_results["ids"][0][i]
                        
                        # Check if this is actually an image
                        content_type = metadata.get("content_type", "")
                        file_type = metadata.get("file_type", "")
                        has_vision = metadata.get("has_vision_analysis", False)
                        
                        is_image = (content_type in ["image", "image_reference"] or 
                                  file_type in ["png", "jpg", "jpeg", "pdf"] or
                                  has_vision)
                        
                        if is_image:
                            result_dict = {
                                "id": doc_id,
                                "text": doc_text,
                                "score": 1.0 - image_results["distances"][0][i],
                                "rank": len(final_results) + 1,
                                "metadata": metadata
                            }
                            final_results.append(result_dict)
                
                # Add relevant text results to fill remaining slots
                remaining_slots = n_results - len(final_results)
                if remaining_slots > 0 and dense_vector_results.get("ids") and dense_vector_results["ids"][0]:
                    for i in range(min(remaining_slots, len(dense_vector_results["ids"][0]))):
                        doc_text = dense_vector_results["documents"][0][i]
                        metadata = dense_vector_results["metadatas"][0][i]
                        doc_id = dense_vector_results["ids"][0][i]
                        
                        # Skip if already added as image
                        if doc_id not in [r["id"] for r in final_results]:
                            result_dict = {
                                "id": doc_id,
                                "text": doc_text,
                                "score": 1.0 - dense_vector_results["distances"][0][i],
                                "rank": len(final_results) + 1,
                                "metadata": metadata
                            }
                            final_results.append(result_dict)
                
                # Log retrieval statistics
                image_count = sum(1 for result in final_results 
                                if result["metadata"].get("content_type") in ["image", "image_reference"] or
                                   result["metadata"].get("has_vision_analysis", False))
                text_count = len(final_results) - image_count
                
                logger.info(f"Image-first retrieval: {text_count} text, {image_count} images")
                
                return final_results
                
            else:
                # Regular hybrid retrieval for non-image queries
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
                
                # Log retrieval statistics
                image_count = sum(1 for result in final_results 
                                if result["metadata"].get("content_type") == "image" or
                                   result["metadata"].get("has_vision_analysis", False))
                text_count = len(final_results) - image_count
                
                logger.info(f"Retrieved {len(final_results)} results for query: {text_count} text, {image_count} images")
                
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
