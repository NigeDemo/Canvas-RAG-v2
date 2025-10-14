"""Integration module for connecting vision AI with the existing RAG system."""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime

from ..retrieval.hybrid_search import HybridSearchEngine, QueryProcessor
from ..generation.vision_enhanced_generator import VisionEnhancedResponseGenerator, VisionEnhancedContext
from ..vision.vision_processor import VisionProcessor
from ..vision.image_analyzer import ImageAnalyzer
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class VisionRAGResult:
    """Result from vision-enhanced RAG query."""
    query: str
    response: str
    text_context: str
    image_references: List[Dict[str, Any]]
    vision_analyses: List[Dict[str, Any]]
    query_type: str
    processing_time: float
    success: bool
    error: Optional[str] = None

class VisionEnhancedRAG:
    """Main vision-enhanced RAG system."""
    
    def __init__(self, 
                 hybrid_search_engine=None,
                 vision_processor=None,
                 response_generator=None):
        """
        Initialize vision-enhanced RAG system.
        
        Args:
            hybrid_search_engine: Hybrid search engine instance
            vision_processor: Vision processor instance
            response_generator: Vision-enhanced response generator
        """
        self.search_engine = hybrid_search_engine
        self.vision_processor = vision_processor or VisionProcessor()
        self.response_generator = response_generator or VisionEnhancedResponseGenerator()
        self.query_processor = QueryProcessor()
        
        # Log initialization status
        search_status = "Available" if self.search_engine else "Not available"
        logger.info(f"Initialized VisionEnhancedRAG system - Search engine: {search_status}")
        
        # Warn if no search engine is available
        if not self.search_engine:
            logger.warning("No search engine available. Only direct image analysis will be supported.")
    
    def query(self, 
              query: str,
              enable_vision: bool = True,
              max_images: int = 3,
              **kwargs) -> VisionRAGResult:
        """
        Process query with vision enhancement.
        
        Args:
            query: User query
            enable_vision: Whether to enable vision analysis
            max_images: Maximum number of images to analyze
            **kwargs: Additional parameters
            
        Returns:
            Vision-enhanced RAG result
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing vision-enhanced query: {query}")
            
            # Analyze query
            query_analysis = self.query_processor.analyze_query(query)
            query_type = query_analysis.get("intent", "factual")
            is_visual_query = query_analysis.get("is_visual_query", False)
            
            # Perform hybrid search
            if self.search_engine:
                search_results = self.search_engine.search(query, **kwargs)
                text_context = self._extract_text_context(search_results)
                image_references = self._extract_image_references(search_results)[:max_images]
            else:
                logger.warning("No search engine available, using empty context")
                text_context = ""
                image_references = []
            
            # Create enhanced context with vision analysis  
            # Only use vision for explicitly visual queries - be more conservative
            explicit_visual_keywords = ['image', 'drawing', 'figure', 'visual', 'analyze', 'examine', 'look at', 'show me', 'what does', 'identify', 'describe the drawing', 'analyze the image']
            has_explicit_visual_intent = any(keyword in query.lower() for keyword in explicit_visual_keywords)
            
            use_vision = enable_vision and (is_visual_query or has_explicit_visual_intent)
            
            if use_vision:
                logger.info(f"Using vision-enhanced response: is_visual_query={is_visual_query}, explicit_visual_intent={has_explicit_visual_intent}")
                enhanced_context = self.response_generator.create_vision_enhanced_context(
                    text_context, image_references, query, query_type
                )
                
                # Generate vision-enhanced response
                response = self.response_generator.generate_vision_enhanced_response(
                    enhanced_context, query
                )
                
                vision_analyses = enhanced_context.vision_analyses
                
            else:
                # Fall back to text-only response
                logger.info(f"Using text-only response: query='{query}', is_visual={is_visual_query}, explicit_visual={has_explicit_visual_intent}")
                response = self._generate_text_only_response(query, text_context, image_references)
                vision_analyses = []
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return VisionRAGResult(
                query=query,
                response=response,
                text_context=text_context,
                image_references=image_references,
                vision_analyses=vision_analyses,
                query_type=query_type,
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error processing vision-enhanced query: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return VisionRAGResult(
                query=query,
                response="I apologize, but I encountered an error processing your query.",
                text_context="",
                image_references=[],
                vision_analyses=[],
                query_type="error",
                processing_time=processing_time,
                success=False,
                error=str(e)
            )
    
    def _extract_text_context(self, search_results) -> str:
        """Extract text context from search results."""
        if not search_results:
            return ""
        
        # Handle different search result formats
        if hasattr(search_results, 'results'):
            results = search_results.results
        elif isinstance(search_results, dict) and 'results' in search_results:
            results = search_results['results']
        elif isinstance(search_results, list):
            results = search_results
        else:
            results = [search_results]
        
        text_chunks = []
        for result in results:
            if hasattr(result, 'text'):
                text_chunks.append(result.text)
            elif isinstance(result, dict) and 'text' in result:
                text_chunks.append(result['text'])
        
        return "\n\n".join(text_chunks)
    
    def _extract_image_references(self, search_results) -> List[Dict[str, Any]]:
        """Extract image references from search results."""
        if not search_results:
            return []

        def normalize_canvas_url(url: Optional[str]) -> str:
            if not url:
                return ""
            url = url.strip()
            if url.startswith("http://") or url.startswith("https://"):
                return url

            base_url = settings.canvas_api_url or ""
            if not base_url:
                return url

            # Remove /api/... segments to get the Canvas host root
            if "/api" in base_url:
                base_url = base_url.split("/api", 1)[0]
            base_url = base_url.rstrip("/")
            url = url.lstrip("/")
            return f"{base_url}/{url}" if base_url else url

        def prefer_canvas_preview(url: str) -> str:
            if not url or "/files/" not in url:
                return url

            base_part, _, query = url.partition("?")

            if "/download" in base_part:
                base_part = base_part.replace("/download", "/preview")
            elif not base_part.endswith("/preview"):
                base_part = base_part.rstrip("/") + "/preview"

            return f"{base_part}?{query}" if query else base_part
        
        # Handle different search result formats
        if hasattr(search_results, 'results'):
            results = search_results.results
        elif isinstance(search_results, dict) and 'results' in search_results:
            results = search_results['results']
        elif isinstance(search_results, list):
            results = search_results
        else:
            results = [search_results]
        
        image_refs = []
        
        logger.info(f"Extracting image references from {len(results)} results")
        
        for i, result in enumerate(results):
            # Check if this result is an image reference
            if hasattr(result, 'metadata'):
                metadata = result.metadata
            elif isinstance(result, dict) and 'metadata' in result:
                metadata = result['metadata']
            else:
                logger.info(f"Result {i}: No metadata found")
                continue
            
            # Check for any image-related content
            content_type = metadata.get('content_type', '')
            has_vision_analysis = metadata.get('has_vision_analysis', False)
            vision_analysis = metadata.get('vision_analysis', '')
            
            logger.info(f"Result {i}: content_type='{content_type}', has_vision_analysis={has_vision_analysis}, vision_analysis_length={len(vision_analysis)}")
            
            # Accept both image and image_reference content types, or anything with vision analysis
            if (content_type in ['image', 'image_reference'] or has_vision_analysis):
                alt_text = metadata.get('alt_text', '')
                logger.info(f"Found image reference: '{alt_text}' with vision analysis length: {len(vision_analysis)}")

                raw_image_url = (metadata.get('image_url') or
                                 metadata.get('file_url') or
                                 metadata.get('url') or
                                 metadata.get('source_url', ''))
                normalized_image_url = prefer_canvas_preview(normalize_canvas_url(raw_image_url))

                source_url = prefer_canvas_preview(normalize_canvas_url(metadata.get('url') or metadata.get('file_url')))

                image_refs.append({
                    'image_url': normalized_image_url,
                    'alt_text': alt_text,
                    'page_title': metadata.get('title', metadata.get('page_title', '')),
                    'parent_module': metadata.get('parent_module', ''),
                    'source_url': source_url,
                    'file_url': prefer_canvas_preview(normalize_canvas_url(metadata.get('file_url'))),
                    'vision_analysis': vision_analysis,
                    'content_type': content_type
                })
        
        logger.info(f"Extracted {len(image_refs)} image references from {len(results)} results")
        return image_refs
    
    def _generate_text_only_response(self, 
                                   query: str, 
                                   text_context: str, 
                                   image_references: List[Dict[str, Any]]) -> str:
        """Generate text-only response using appropriate template."""
        # Handle case where no search engine is available
        if not text_context and not image_references:
            return f"""I apologize, but I don't have access to any course content to answer your question about "{query}".

This could be because:
1. The search engine is not properly initialized
2. No course content has been indexed yet
3. The Canvas integration is not configured

To get meaningful responses, please:
1. Ensure your Canvas API credentials are configured
2. Run the content ingestion pipeline to index course materials
3. Try uploading an image directly for analysis

You can still use the direct image analysis feature by uploading an image in the sidebar."""
        
        # Analyze query to determine intent (use QueryProcessor)
        query_analysis = self.query_processor.analyze_query(query)
        intent = query_analysis.get('intent', 'factual')
        
        logger.info(f"Generating text-only response with intent: {intent}")
        
        # Format image references for text-only response
        image_list = []
        for i, img_ref in enumerate(image_references, 1):
            alt_text = img_ref.get('alt_text', 'Unknown')
            url = img_ref.get('image_url', '#')
            page_title = img_ref.get('page_title', '')
            
            if page_title:
                image_list.append(f"{i}. [{alt_text}]({url}) - From: {page_title}")
            else:
                image_list.append(f"{i}. [{alt_text}]({url})")
        
        formatted_images = "\n".join(image_list) if image_list else "No images available."
        
        # Add images to context if available
        context_with_images = text_context if text_context else "No text context available."
        if image_list:
            context_with_images += f"\n\nAvailable Images:\n{formatted_images}"
        else:
            context_with_images += "\n\nAvailable Images:\nNo images were retrieved in the current search results."
        
        # Use ResponseGenerator with appropriate template
        try:
            # Get the template from ResponseGenerator (it has our module-aware templates)
            from ..generation.llm_integration import PromptTemplate
            
            template_manager = PromptTemplate()
            template = template_manager.templates.get(intent, template_manager.templates['factual'])
            
            # Format the prompt with context
            prompt = template.format(context=context_with_images, query=query)
            
            return self.response_generator.llm_provider.generate_response(prompt)
        except Exception as e:
            logger.error(f"Error generating text-only response: {e}")
            return "I apologize, but I encountered an error generating a response. Please check your API configuration."
    
    def batch_query(self, 
                   queries: List[str],
                   enable_vision: bool = True,
                   **kwargs) -> List[VisionRAGResult]:
        """
        Process multiple queries with vision enhancement.
        
        Args:
            queries: List of user queries
            enable_vision: Whether to enable vision analysis
            **kwargs: Additional parameters
            
        Returns:
            List of vision-enhanced RAG results
        """
        results = []
        
        for i, query in enumerate(queries):
            logger.info(f"Processing query {i+1}/{len(queries)}: {query}")
            result = self.query(query, enable_vision=enable_vision, **kwargs)
            results.append(result)
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all system components."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "search_engine": self.search_engine is not None,
            "vision_processor": self.vision_processor.get_provider_status() if self.vision_processor else {},
            "response_generator": self.response_generator is not None
        }
        
        return status
    
    def analyze_image_directly(self, 
                             image_input,
                             query: str,
                             analysis_type: str = "query_specific") -> Dict[str, Any]:
        """
        Analyze single image directly without retrieval.
        
        Args:
            image_input: Image data (URL, file path, or bytes)
            query: User query about the image
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        try:
            image_analyzer = ImageAnalyzer(self.vision_processor)
            
            result = image_analyzer.analyze_image(
                image_input, 
                analysis_type=analysis_type,
                query=query
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in direct image analysis: {e}")
            return {
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def extract_text_from_image(self, image_input) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image_input: Image data (URL, file path, or bytes)
            
        Returns:
            Extracted text
        """
        try:
            return self.vision_processor.extract_text(image_input)
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def describe_image(self, image_input) -> str:
        """
        Generate description of image.
        
        Args:
            image_input: Image data (URL, file path, or bytes)
            
        Returns:
            Image description
        """
        try:
            return self.vision_processor.describe_image(image_input)
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return ""

# Factory function for easy initialization
def create_vision_rag_system(search_engine=None) -> VisionEnhancedRAG:
    """
    Create a vision-enhanced RAG system with default configuration.
    
    Args:
        search_engine: Optional existing search engine
        
    Returns:
        Configured VisionEnhancedRAG system
    """
    try:
        # Initialize vision processor
        vision_processor = VisionProcessor(
            primary_provider=getattr(settings, 'vision_primary_provider', 'openai'),
            fallback_provider=getattr(settings, 'vision_fallback_provider', 'claude'),
            use_cache=getattr(settings, 'vision_cache_enabled', True),
            cache_ttl_hours=getattr(settings, 'vision_cache_ttl_hours', 24)
        )
        
        # Initialize response generator
        response_generator = VisionEnhancedResponseGenerator(
            vision_processor=vision_processor
        )
        
        # Create the system
        vision_rag = VisionEnhancedRAG(
            hybrid_search_engine=search_engine,
            vision_processor=vision_processor,
            response_generator=response_generator
        )
        
        logger.info("Vision RAG system created successfully")
        return vision_rag
        
    except Exception as e:
        logger.error(f"Error creating vision RAG system: {e}")
        
        # Try to create a minimal system that can at least do direct image analysis
        try:
            logger.warning("Attempting to create minimal vision RAG system")
            
            # Create basic vision processor
            vision_processor = VisionProcessor()
            
            # Create basic response generator
            response_generator = VisionEnhancedResponseGenerator()
            
            # Create minimal system
            vision_rag = VisionEnhancedRAG(
                hybrid_search_engine=search_engine,
                vision_processor=vision_processor,
                response_generator=response_generator
            )
            
            logger.info("Minimal vision RAG system created")
            return vision_rag
            
        except Exception as e2:
            logger.error(f"Failed to create minimal vision RAG system: {e2}")
            raise RuntimeError(f"Could not create vision RAG system: {e}")
            
        raise
