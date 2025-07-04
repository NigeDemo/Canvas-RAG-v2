"""Hybrid search engine for combining dense and sparse retrieval."""

from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass

from ..indexing.vector_store import HybridRetriever
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SearchResult:
    """Represents a search result."""
    id: str
    text: str
    score: float
    rank: int
    metadata: Dict[str, Any]
    highlighted_text: Optional[str] = None

class QueryProcessor:
    """Processes and analyzes user queries."""
    
    def __init__(self):
        """Initialize query processor."""
        # Architectural drawing keywords
        self.drawing_keywords = {
            'plan': ['floor plan', 'site plan', 'plan view', 'layout'],
            'section': ['section', 'sectional', 'cross section', 'section cut'],
            'elevation': ['elevation', 'facade', 'front view', 'side view'],
            'detail': ['detail', 'detailed', 'close-up', 'construction detail'],
            'perspective': ['perspective', '3d view', 'isometric', 'axonometric'],
            'scale': ['scale', 'scaling', 'dimension', 'measurement'],
            'annotation': ['annotation', 'label', 'text', 'callout'],
            'dimensioning': ['dimension', 'dimensioning', 'measurement line'],
            'hatching': ['hatching', 'pattern', 'fill', 'cross-hatching'],
            'symbols': ['symbol', 'notation', 'legend', 'key']
        }
        
        # Question type patterns
        self.question_patterns = {
            'what': r'\b(what|which)\b.*\?',
            'how': r'\bhow\b.*\?',
            'where': r'\bwhere\b.*\?',
            'when': r'\bwhen\b.*\?',
            'why': r'\bwhy\b.*\?',
            'scale': r'\b(scale|dimension|size|measurement)\b',
            'visual': r'\b(show|display|image|drawing|figure|diagram)\b'
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to understand intent and extract keywords.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with query analysis
        """
        query_lower = query.lower()
        
        analysis = {
            'original_query': query,
            'normalized_query': query_lower,
            'drawing_types': [],
            'question_type': 'general',
            'is_visual_query': False,
            'keywords': [],
            'intent': 'factual'
        }
        
        # Detect drawing types
        for drawing_type, keywords in self.drawing_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    analysis['drawing_types'].append(drawing_type)
                    analysis['keywords'].append(keyword)
        
        # Detect question type
        for q_type, pattern in self.question_patterns.items():
            if re.search(pattern, query_lower):
                analysis['question_type'] = q_type
                break
        
        # Detect visual queries
        if re.search(self.question_patterns['visual'], query_lower):
            analysis['is_visual_query'] = True
            analysis['intent'] = 'visual_reasoning'
        
        # Detect scale/measurement queries
        if re.search(self.question_patterns['scale'], query_lower):
            analysis['intent'] = 'measurement'
        
        logger.debug(f"Query analysis: {analysis}")
        return analysis

class ResultProcessor:
    """Processes and enhances search results."""
    
    def __init__(self):
        """Initialize result processor."""
        pass
    
    def highlight_query_terms(self, text: str, query_terms: List[str], max_length: int = 500) -> str:
        """
        Highlight query terms in text and create snippet.
        
        Args:
            text: Text to highlight
            query_terms: Terms to highlight
            max_length: Maximum length of snippet
            
        Returns:
            Highlighted text snippet
        """
        if not text or not query_terms:
            return text[:max_length] if text else ""
        
        # Find best snippet containing query terms
        text_lower = text.lower()
        best_start = 0
        max_matches = 0
        
        # Look for sections with most query term matches
        for i in range(0, len(text) - max_length + 1, 50):
            snippet = text_lower[i:i + max_length]
            matches = sum(1 for term in query_terms if term.lower() in snippet)
            if matches > max_matches:
                max_matches = matches
                best_start = i
        
        snippet = text[best_start:best_start + max_length]
        
        # Highlight terms
        highlighted = snippet
        for term in query_terms:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted = pattern.sub(f"**{term}**", highlighted)
        
        # Add ellipsis if truncated
        if best_start > 0:
            highlighted = "..." + highlighted
        if best_start + max_length < len(text):
            highlighted = highlighted + "..."
        
        return highlighted
    
    def group_results_by_source(self, results: List[SearchResult]) -> Dict[str, List[SearchResult]]:
        """
        Group results by source document/page.
        
        Args:
            results: List of search results
            
        Returns:
            Dictionary with results grouped by source
        """
        grouped = {}
        
        for result in results:
            source_key = result.metadata.get('source_id', 'unknown')
            if result.metadata.get('source_type') == 'page':
                source_key = f"page_{source_key}"
            elif result.metadata.get('source_type') == 'file':
                source_key = f"file_{result.metadata.get('filename', source_key)}"
            
            if source_key not in grouped:
                grouped[source_key] = []
            grouped[source_key].append(result)
        
        return grouped
    
    def rank_sources_by_relevance(self, grouped_results: Dict[str, List[SearchResult]]) -> List[Tuple[str, List[SearchResult]]]:
        """
        Rank source groups by cumulative relevance.
        
        Args:
            grouped_results: Results grouped by source
            
        Returns:
            List of (source_key, results) tuples ranked by relevance
        """
        source_scores = []
        
        for source_key, results in grouped_results.items():
            # Calculate cumulative score for source
            total_score = sum(result.score for result in results)
            avg_score = total_score / len(results)
            
            # Boost sources with multiple relevant segments
            boosted_score = total_score + (len(results) - 1) * 0.1
            
            source_scores.append((source_key, results, boosted_score))
        
        # Sort by boosted score
        source_scores.sort(key=lambda x: x[2], reverse=True)
        
        return [(source_key, results) for source_key, results, _ in source_scores]

class HybridSearchEngine:
    """Main search engine coordinating retrieval and processing."""
    
    def __init__(self, retriever: HybridRetriever):
        """
        Initialize search engine.
        
        Args:
            retriever: HybridRetriever instance
        """
        self.retriever = retriever
        self.query_processor = QueryProcessor()
        self.result_processor = ResultProcessor()
        
        logger.info("Initialized hybrid search engine")
    
    def search(self, query: str, n_results: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Perform comprehensive search.
        
        Args:
            query: User query
            n_results: Number of results to return
            **kwargs: Additional search parameters
            
        Returns:
            Comprehensive search results
        """
        try:
            logger.info(f"Searching for: {query}")
            
            # Analyze query
            query_analysis = self.query_processor.analyze_query(query)
            
            # Perform retrieval
            raw_results = self.retriever.retrieve(query, n_results)
            
            if not raw_results:
                logger.warning("No results found")
                return {
                    'query': query,
                    'query_analysis': query_analysis,
                    'results': [],
                    'total_results': 0,
                    'grouped_results': {},
                    'ranked_sources': []
                }
            
            # Convert to SearchResult objects
            search_results = []
            query_terms = query.split()
            
            for result_dict in raw_results:
                highlighted_text = self.result_processor.highlight_query_terms(
                    result_dict['text'], 
                    query_terms
                )
                
                search_result = SearchResult(
                    id=result_dict['id'],
                    text=result_dict['text'],
                    score=result_dict['score'],
                    rank=result_dict['rank'],
                    metadata=result_dict['metadata'],
                    highlighted_text=highlighted_text
                )
                search_results.append(search_result)
            
            # Group and rank results
            grouped_results = self.result_processor.group_results_by_source(search_results)
            ranked_sources = self.result_processor.rank_sources_by_relevance(grouped_results)
            
            search_response = {
                'query': query,
                'query_analysis': query_analysis,
                'results': search_results,
                'total_results': len(search_results),
                'grouped_results': grouped_results,
                'ranked_sources': ranked_sources
            }
            
            logger.info(f"Search completed. Found {len(search_results)} results from {len(grouped_results)} sources")
            return search_response
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return {
                'query': query,
                'error': str(e),
                'results': [],
                'total_results': 0
            }
    
    def search_by_content_type(self, query: str, content_types: List[str], n_results: int = 10) -> Dict[str, Any]:
        """
        Search filtered by content types.
        
        Args:
            query: User query
            content_types: List of content types to filter by
            n_results: Number of results to return
            
        Returns:
            Filtered search results
        """
        # This would require implementing metadata filtering in the retriever
        # For now, perform regular search and filter results
        search_results = self.search(query, n_results * 2)
        
        filtered_results = [
            result for result in search_results['results']
            if result.metadata.get('content_type') in content_types
        ]
        
        search_results['results'] = filtered_results[:n_results]
        search_results['total_results'] = len(filtered_results)
        
        return search_results
