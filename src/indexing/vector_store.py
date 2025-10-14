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

def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize metadata for ChromaDB by removing None values and ensuring valid types.
    
    ChromaDB only accepts: bool, int, float, str, or sparse vectors.
    None values cause TypeError.
    
    Args:
        metadata: Original metadata dictionary
        
    Returns:
        Sanitized metadata dictionary
    """
    sanitized = {}
    for key, value in metadata.items():
        if value is None:
            # Skip None values entirely
            continue
        elif isinstance(value, (bool, int, float, str)):
            # Valid types - keep as is
            sanitized[key] = value
        elif isinstance(value, (list, tuple)):
            # Convert lists/tuples to strings
            sanitized[key] = str(value)
        elif isinstance(value, dict):
            # Convert dicts to JSON strings
            sanitized[key] = json.dumps(value)
        else:
            # Convert any other type to string
            sanitized[key] = str(value)
    
    return sanitized

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
            
            # Sanitize metadata to remove None values
            sanitized_metadata = [sanitize_metadata(meta) for meta in metadata]
            
            # Convert numpy array to list for ChromaDB
            embeddings_list = embeddings.tolist()
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings_list,
                metadatas=sanitized_metadata,
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
        
        # More conservative image detection - require explicit visual intent
        explicit_visual_keywords = [
            'show me the image', 'show me the drawing', 'show me the plan',
            'describe the image', 'describe the drawing', 'describe the plan',
            'analyze the image', 'analyze the drawing', 'analyze the plan',
            'examine the image', 'examine the drawing', 'examine the plan',
            'what does the image', 'what does the drawing', 'what does the plan',
            'identify in the image', 'identify in the drawing', 'identify in the plan',
            'look at the image', 'look at the drawing', 'look at the plan',
            'what can you see', 'what is visible', 'what appears in'
        ]
        
        # Check for explicit visual phrases first
        for phrase in explicit_visual_keywords:
            if phrase in query_lower:
                return True

        # Broader detection for list/show requests that mention images or drawings
        image_nouns = ['image', 'images', 'drawing', 'drawings', 'diagram', 'diagrams', 'plan', 'plans', 'visual', 'visuals', 'render', 'renders']
        request_verbs = ['list', 'show', 'display', 'provide', 'share', 'give', 'find', 'see', 'available', 'include', 'pull', 'fetch']

        if any(noun in query_lower for noun in image_nouns):
            if any(verb in query_lower for verb in request_verbs):
                return True
            # Questions like "what images" or "which drawings" should still count
            if query_lower.strip().startswith(('what', 'which')):
                return True
        
        # Check for visual analysis patterns only when combined with explicit visual request
        visual_patterns = [
            r'\b(show|display).*(image|drawing|plan|diagram)',
            r'\b(describe|analyze|examine|identify).*(this|the).*(image|drawing|plan|diagram)',
            r'\bcan you (see|find|identify|describe).*(image|drawing|plan|diagram)',
            r'\bwhat.*(visible|appears|shown).*(image|drawing|plan|diagram)',
        ]
        
        for pattern in visual_patterns:
            if re.search(pattern, query_lower):
                return True
        
        # Don't trigger on general questions about topics, purposes, or overviews        
        general_question_patterns = [
            r'\bwhat.*topics.*covered',
            r'\bwhat.*purpose.*page',
            r'\bwhat.*about.*page',
            r'\boverview.*of',
            r'\bsummary.*of',
            r'\btopics.*discussed',
            r'\bwhat.*includes',
            r'\bwhat.*contains'
        ]
        
        for pattern in general_question_patterns:
            if re.search(pattern, query_lower):
                return False
                
        return False
    
    def is_section_heading_query(self, query: str) -> bool:
        """Detect if query is asking about section headings or page structure."""
        query_lower = query.lower()
        
        # Patterns that indicate requests for section structure
        section_heading_patterns = [
            r'\bwhat.*sections.*on.*page',
            r'\bwhat.*sections.*covered',
            r'\bwhat.*topics.*covered',
            r'\bwhat.*headings.*on.*page',
            r'\bwhat.*headings.*in.*document',
            r'\blist.*sections',
            r'\blist.*headings',
            r'\btitles.*sections',
            r'\bsection.*titles',
            r'\bpage.*structure',
            r'\bdocument.*structure',
            r'\bmain.*topics.*discussed',
            r'\bmain.*sections.*in',
            r'\boverview.*topics',
            r'\btable.*contents',
            r'\bwhat.*organized.*into',
            r'\bhow.*organized',
            r'\bwhat.*parts.*include',
            r'\bwhat.*divided.*into'
        ]
        
        for pattern in section_heading_patterns:
            if re.search(pattern, query_lower):
                return True
        
        # Also check for direct title-related queries
        title_patterns = [
            r'\btitle.*page',
            r'\bpage.*title',
            r'\bname.*page',
            r'\bwhat.*called',
            r'\bwhat.*page.*about'
        ]
        
        for pattern in title_patterns:
            if re.search(pattern, query_lower):
                return True
                
        return False
    
    def _looks_like_section_heading(self, text: str) -> bool:
        """Check if text looks like a section heading."""
        if not text or len(text) > 300:  # Too long to be a heading
            return False
        
        text_clean = text.strip()
        
        # Check for question patterns (common in our content)
        if re.match(r'^.{10,200}\?$', text_clean):
            return True
        
        # Check for title-case patterns
        if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s*$', text_clean):
            return True
        
        # Check for heading patterns in content
        lines = text_clean.split('\n')
        first_line = lines[0].strip() if lines else ""
        
        # First line looks like a heading
        if (first_line and 
            len(first_line) < 200 and 
            (first_line.endswith('?') or 
             re.match(r'^[A-Z].*[a-z]$', first_line))):
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
    
    def reciprocal_rank_fusion(self, 
                              dense_results: List[Tuple[int, float]], 
                              sparse_results: List[Tuple[int, float]], 
                              k: int = 60) -> List[Tuple[int, float, str]]:
        """
        Combine dense and sparse results using reciprocal rank fusion.
        
        Args:
            dense_results: List of (index, score) from dense retrieval
            sparse_results: List of (index, score) from sparse retrieval
            k: RRF constant (typically 60)
            
        Returns:
            List of (index, fused_score, source) tuples
        """
        fused_scores = {}
        
        # Process dense results
        for rank, (idx, score) in enumerate(dense_results, start=1):
            rrf_score = 1.0 / (k + rank)
            fused_scores[idx] = {
                'score': self.alpha * rrf_score,
                'dense_rank': rank,
                'sparse_rank': None,
                'source': 'dense'
            }
        
        # Process sparse results
        for rank, (idx, score) in enumerate(sparse_results, start=1):
            rrf_score = 1.0 / (k + rank)
            if idx in fused_scores:
                # Document appears in both - add scores
                fused_scores[idx]['score'] += (1 - self.alpha) * rrf_score
                fused_scores[idx]['sparse_rank'] = rank
                fused_scores[idx]['source'] = 'hybrid'
            else:
                # Document only in sparse results
                fused_scores[idx] = {
                    'score': (1 - self.alpha) * rrf_score,
                    'dense_rank': None,
                    'sparse_rank': rank,
                    'source': 'sparse'
                }
        
        # Sort by fused score
        sorted_results = sorted(fused_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Return as list of (index, score, source) tuples
        return [(idx, info['score'], info['source']) for idx, info in sorted_results]
    
    def retrieve(
        self,
        query: str,
        n_results: int = 10,
        *,
        original_query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval with image boosting.
        
        Args:
            query: Query string
            n_results: Number of results to return
            
        Returns:
            List of retrieved document dictionaries
        """
        try:
            # Use the original query (pre-enhancement) for intent detection when available
            analysis_query = original_query or query

            # Check if this is an image query
            is_image_query = self.is_image_query(analysis_query)
            
            # Check if this is a section heading query
            is_section_query = self.is_section_heading_query(analysis_query)
            
            # Handle section heading queries specially
            if is_section_query:
                logger.info(f"Section heading query detected, prioritizing section headings")
                
                # For section queries, get ALL section headings first, then add other content
                all_collection_results = self.vector_store.collection.get()
                
                final_results = []
                section_headings = []
                
                # First, collect all section headings directly from the collection
                for i, metadata in enumerate(all_collection_results['metadatas']):
                    if (metadata.get('content_type') == 'section_heading' or 
                        metadata.get('is_section_heading', False)):
                        
                        section_headings.append({
                            "id": all_collection_results['ids'][i],
                            "text": all_collection_results['documents'][i],
                            "score": 1.0,  # Give high score to section headings
                            "rank": len(section_headings) + 1,
                            "metadata": metadata
                        })
                
                # Add all section headings first
                final_results.extend(section_headings)
                
                # If we need more results, get additional content via vector search
                if len(final_results) < n_results:
                    query_embedding = self.embedding_manager.embed_query(query)
                    additional_results = self.vector_store.query(
                        query_embedding, 
                        n_results - len(final_results)
                    )
                    
                    # Add non-heading results
                    if additional_results.get("ids") and additional_results["ids"][0]:
                        for i in range(len(additional_results["ids"][0])):
                            doc_id = additional_results["ids"][0][i]
                            doc_text = additional_results["documents"][0][i]
                            metadata = additional_results["metadatas"][0][i]
                            
                            # Skip if it's already a section heading we added
                            if not (metadata.get('content_type') == 'section_heading' or 
                                   metadata.get('is_section_heading', False)):
                                
                                final_results.append({
                                    "id": doc_id,
                                    "text": doc_text,
                                    "score": 1.0 - additional_results["distances"][0][i],
                                    "rank": len(final_results) + 1,
                                    "metadata": metadata
                                })
                
                logger.info(f"Section query results: {len(section_headings)} headings, {len(final_results) - len(section_headings)} other content")
                return final_results[:n_results]
            
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
                logger.debug(f"Regular hybrid retrieval for query: '{query}'")
                
                # 1. Dense retrieval (vector search)
                query_embedding = self.embedding_manager.embed_query(query)
                dense_vector_results = self.vector_store.query(query_embedding, n_results * 2)
                
                # Convert ChromaDB results to (index, similarity) format
                dense_results = []
                if dense_vector_results.get("ids") and dense_vector_results["ids"][0]:
                    for i, distance in enumerate(dense_vector_results["distances"][0]):
                        # Convert distance to similarity score (assuming cosine distance)
                        similarity = 1.0 - distance
                        dense_results.append((i, similarity))
                    logger.debug(f"Dense retrieval: {len(dense_results)} results")
                else:
                    logger.warning("No dense results returned")
                
                # 2. Sparse retrieval (BM25)
                sparse_results = []
                if self.sparse_index.is_initialized:
                    sparse_results = self.sparse_index.query(query, n_results * 2)
                    logger.debug(f"BM25 sparse retrieval: {len(sparse_results)} results")
                else:
                    logger.warning("BM25 index not initialized - using dense-only retrieval")
                
                # 3. Fusion
                if dense_results and sparse_results:
                    logger.info(f"Hybrid fusion: {len(dense_results)} dense + {len(sparse_results)} sparse results")
                    fused_results = self.reciprocal_rank_fusion(dense_results, sparse_results)
                    
                    # Log fusion statistics
                    hybrid_count = sum(1 for _, _, source in fused_results if source == 'hybrid')
                    dense_only = sum(1 for _, _, source in fused_results if source == 'dense')
                    sparse_only = sum(1 for _, _, source in fused_results if source == 'sparse')
                    logger.info(f"Fusion results: {hybrid_count} hybrid, {dense_only} dense-only, {sparse_only} sparse-only")
                    
                elif dense_results:
                    logger.info("Using dense-only retrieval (no sparse results)")
                    fused_results = [(i, score, 'dense') for i, score in dense_results]
                elif sparse_results:
                    logger.info("Using sparse-only retrieval (no dense results)")
                    fused_results = [(i, score, 'sparse') for i, score in sparse_results]
                else:
                    logger.warning("No results from either dense or sparse retrieval")
                    return []
                
                # 4. Prepare final results
                final_results = []
                for rank, (result_idx, score, source) in enumerate(fused_results[:n_results]):
                    doc_id = None
                    doc_text = None
                    metadata = None
                    
                    # Get document data based on source
                    if source in ['dense', 'hybrid']:
                        # Try to get from dense results
                        if result_idx < len(dense_vector_results.get("documents", [[]])[0]):
                            doc_text = dense_vector_results["documents"][0][result_idx]
                            metadata = dense_vector_results["metadatas"][0][result_idx]
                            doc_id = dense_vector_results["ids"][0][result_idx]
                    
                    if doc_text is None and source in ['sparse', 'hybrid']:
                        # Try to get from sparse results
                        if result_idx < len(self.sparse_index.documents):
                            doc_text = self.sparse_index.documents[result_idx]
                            metadata = self.sparse_index.metadata[result_idx]
                            doc_id = metadata.get('id', f"sparse_{result_idx}")
                    
                    if doc_text and metadata:
                        result_dict = {
                            "id": doc_id,
                            "text": doc_text,
                            "score": score,
                            "rank": rank + 1,
                            "metadata": metadata,
                            "retrieval_source": source  # Track which retrieval method found this
                        }
                        final_results.append(result_dict)
                
                # Log retrieval statistics
                image_count = sum(1 for result in final_results 
                                if result["metadata"].get("content_type") in ["image", "image_reference"] or
                                   result["metadata"].get("has_vision_analysis", False))
                text_count = len(final_results) - image_count
                
                logger.info(f"Retrieved {len(final_results)} results: {text_count} text, {image_count} images")
                
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
        
        # Auto-populate sparse index from existing ChromaDB content
        self._populate_sparse_index_from_existing()
        
        self.retriever = HybridRetriever(
            self.vector_store,
            self.sparse_index,
            self.embedding_manager,
            alpha=settings.hybrid_fusion_alpha
        )
        
        logger.info("Initialized index builder")
    
    def _populate_sparse_index_from_existing(self):
        """Populate sparse index from existing ChromaDB content."""
        try:
            collection = self.vector_store.client.get_collection(name=self.vector_store.collection_name)
            all_docs = collection.get()
            
            # Filter for text content only (including section-aware content)
            text_documents = []
            text_metadata = []
            
            for doc, metadata in zip(all_docs['documents'], all_docs['metadatas']):
                content_type = metadata.get('content_type', '')
                # Include text_chunk, section_content, and section_heading
                if content_type in ['text_chunk', 'section_content', 'section_heading'] and doc and len(doc.strip()) > 0:
                    text_documents.append(doc)
                    text_metadata.append(metadata)
            
            if text_documents:
                self.sparse_index.add_documents(text_documents, text_metadata)
                logger.info(f"✅ Auto-populated BM25 sparse index with {len(text_documents)} text documents")
                logger.debug(f"   Content types: text_chunk, section_content, section_heading")
            else:
                logger.warning("⚠️ No text documents found to populate sparse index")
                
        except Exception as e:
            logger.warning(f"Could not auto-populate sparse index: {e}")
    
    def get_retriever(self):
        """Get the hybrid retriever."""
        return self.retriever
    
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
        
        # Separate lists for sparse index (text only)
        sparse_documents = []
        sparse_metadata = []
        
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
                
                # Add text content to sparse index
                content_type = segment.get('content_type', '')
                if content_type in ['text_chunk', 'section_content', 'section_heading']:
                    sparse_documents.append(doc_text)
                    sparse_metadata.append(segment)
        
        if not documents:
            logger.warning("No documents to index")
            return
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedding_manager.embed_content(content_for_embedding)
        
        # Add to vector store
        logger.info("Adding documents to vector store...")
        self.vector_store.add_documents(documents, embeddings, metadata)
        
        # Build BM25 sparse index with text documents only
        logger.info(f"Building BM25 sparse index with {len(sparse_documents)} text documents...")
        if sparse_documents:
            # Clear existing sparse index and rebuild
            self.sparse_index = SparseIndex()
            self.sparse_index.add_documents(sparse_documents, sparse_metadata)
            
            # Update retriever with new sparse index
            self.retriever.sparse_index = self.sparse_index
            
            logger.info(f"✅ BM25 sparse index built successfully with {len(sparse_documents)} documents")
        else:
            logger.warning("⚠️ No text documents found for BM25 indexing")
        
        logger.info(f"Index building complete. Vector store: {len(documents)} documents, BM25 index: {len(sparse_documents)} text documents")
    
    def get_retriever(self) -> HybridRetriever:
        """Get the hybrid retriever instance."""
        return self.retriever
