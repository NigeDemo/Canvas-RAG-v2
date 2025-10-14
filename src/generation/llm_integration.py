"""LLM integration and response generation."""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..config.settings import settings
from ..retrieval.hybrid_search import SearchResult
from ..utils.logger import get_logger

logger = get_logger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    def generate_multimodal_response(self, prompt: str, images: List[str] = None, **kwargs) -> str:
        """Generate response with multimodal input."""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, model: str = None, api_key: str = None):
        """
        Initialize OpenAI provider.
        
        Args:
            model: Model name
            api_key: OpenAI API key
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package is required")
        
        self.model = model or settings.openai_model
        self.client = openai.OpenAI(api_key=api_key or settings.openai_api_key)
        
        logger.info(f"Initialized OpenAI provider with model: {self.model}")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate text response using OpenAI.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return "I apologize, but I encountered an error generating a response."
    
    def generate_multimodal_response(self, prompt: str, images: List[str] = None, **kwargs) -> str:
        """
        Generate response with vision capabilities.
        
        Args:
            prompt: Text prompt
            images: List of base64 encoded images
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            messages = []
            
            # Add text prompt
            content = [{"type": "text", "text": prompt}]
            
            # Add images if provided
            if images:
                for image_b64 in images[:5]:  # Limit to 5 images
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                            "detail": "auto"
                        }
                    })
            
            messages.append({"role": "user", "content": content})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating multimodal response: {e}")
            return "I apologize, but I encountered an error processing the visual content."

class PromptTemplate:
    """Manages prompt templates for different query types."""
    
    def __init__(self):
        """Initialize prompt templates."""
        self.templates = {
            'factual': """You are an expert assistant helping architecture students with technical questions about architectural drawings and design.

Context: The following content was retrieved from Canvas course materials about architectural drawing techniques:

{context}

Student Question: {query}

Instructions:
- Provide a clear, accurate answer based on the context provided
- If referencing specific images or drawings, mention them explicitly
- Include relevant Canvas links when available
- If the information isn't in the context, say so clearly
- Focus on practical application for architecture students

Answer:""",

            'module_content': """You are an expert assistant helping architecture students navigate their Canvas course modules.

Important Note About Canvas Course Structure:
- Files and materials are placed in Canvas modules by the instructor for when students need them
- Prep materials for upcoming sessions may appear in earlier modules
- For example: "Session 5" prep materials may be in the "Session 4" module
- The module structure reflects teaching logistics, not just content naming

Context: The following content was retrieved from Canvas course materials:

{context}

Student Question: {query}

Instructions:
- Answer based on what's actually IN the specified Canvas module, not what the files are named
- If you find prep materials (files for future sessions) in the module, mention them clearly
- Distinguish between: 
  1. Main module content (what's taught that week)
  2. Prep materials (content for upcoming sessions)
- Explain if materials for a session are split across modules
- Include Canvas module names and file names in your response
- Be specific about what students will find where

Answer:""",

                        'module_image_listing': """You are an expert assistant helping architecture students locate the exact drawings and images inside their Canvas modules.

Important Note About Canvas Course Structure:
- Files and materials may be organized in earlier modules as prep for a later session
- Image references often live alongside text chunks and vision analysis metadata
- Students need clickable links to open the actual drawings in Canvas

Context: The following content was retrieved from Canvas course materials (including any image references):

{context}

Student Question: {query}

Instructions:
- List every relevant image or drawing actually found in the retrieved context
- For each item include: drawing title/description, Canvas module name, and a clickable link
- If vision analysis text is available, summarize what the drawing shows in one sentence
- Group results by module when possible so students know where to click in Canvas
- If no images were retrieved, state that clearly and suggest checking the specific module or re-running ingestion
- Do not invent images—only reference entries that include real Canvas URLs

Answer:""",

            'visual_reasoning': """You are an expert in architectural drawing analysis helping students understand visual elements in technical drawings.

Context: The following content and images were retrieved from Canvas course materials:

{context}

Student Question: {query}

Instructions:
- Analyze the visual content in the context of the question
- Describe what can be seen in relevant images or drawings
- Explain the technical aspects shown in the visuals
- Reference specific drawing elements, scales, or techniques
- Provide Canvas links to original sources
- If asking about images not visible in the context, explain what's needed

Visual Analysis and Answer:""",

            'measurement': """You are an expert in architectural drawing standards and dimensioning helping students with scale and measurement questions.

Context: The following content about drawing standards and measurements was retrieved:

{context}

Student Question: {query}

Instructions:
- Focus on scales, dimensions, and measurement standards
- Explain appropriate scales for different drawing types
- Reference any specific measurement guidelines shown
- Include information about drawing conventions
- Provide practical examples when possible
- Link back to original Canvas sources

Technical Answer:""",

            'general': """You are a helpful assistant for architecture students studying technical drawing and design.

Context from Canvas course materials:

{context}

Student Question: {query}

Please provide a helpful answer based on the context provided. Include references to original sources when possible.

Answer:"""
        }
    
    def get_template(self, intent: str) -> str:
        """Get prompt template for specific intent."""
        return self.templates.get(intent, self.templates['general'])

class ResponseGenerator:
    """Generates responses using LLM and retrieved context."""
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize response generator.
        
        Args:
            llm_provider: LLM provider instance
        """
        self.llm_provider = llm_provider
        self.prompt_template = PromptTemplate()
        
        logger.info("Initialized response generator")
    
    def format_context(self, search_results: List[SearchResult]) -> str:
        """
        Format search results into context string.
        
        Args:
            search_results: List of search results
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, result in enumerate(search_results[:5], 1):  # Limit to top 5 results
            metadata = result.metadata
            
            # Create source information
            source_info = []
            
            # Add Canvas module information if available
            if metadata.get('parent_module'):
                source_info.append(f"Canvas Module: {metadata['parent_module']}")
            
            if metadata.get('source_type') == 'page':
                source_info.append(f"Page: {metadata.get('title', 'Unknown')}")
                if metadata.get('url'):
                    source_info.append(f"Link: {metadata['url']}")
            elif metadata.get('source_type') == 'file':
                source_info.append(f"File: {metadata.get('filename', 'Unknown')}")
                if metadata.get('page_number'):
                    source_info.append(f"Page {metadata['page_number']}")
                elif metadata.get('slide_number'):
                    source_info.append(f"Slide {metadata['slide_number']}")
                if metadata.get('file_url'):
                    source_info.append(f"Link: {metadata['file_url']}")
            
            # Format content
            content_part = f"[Source {i}] {' | '.join(source_info)}\n"
            
            # Add text content
            if result.highlighted_text:
                content_part += f"Content: {result.highlighted_text}\n"
            else:
                content_part += f"Content: {result.text[:500]}...\n"
            
            # Add image information if present
            if metadata.get('content_type') in ['pdf_page', 'image', 'pptx_slide']:
                content_part += "[Note: This source contains visual content - images or drawings]\n"
            
            content_part += f"Relevance Score: {result.score:.3f}\n"
            context_parts.append(content_part)
        
        return "\n---\n".join(context_parts)
    
    def extract_images_from_results(self, search_results: List[SearchResult]) -> List[str]:
        """
        Extract base64 images from search results.
        
        Args:
            search_results: List of search results
            
        Returns:
            List of base64 encoded images
        """
        images = []
        
        for result in search_results:
            metadata = result.metadata
            if 'image_base64' in metadata:
                images.append(metadata['image_base64'])
        
        return images
    
    def generate_response(self, 
                         query: str, 
                         search_results: List[SearchResult], 
                         query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive response to user query.
        
        Args:
            query: User query
            search_results: Retrieved search results
            query_analysis: Query analysis from search engine
            
        Returns:
            Response dictionary with answer and metadata
        """
        try:
            # Format context
            context = self.format_context(search_results)
            
            # Get appropriate prompt template
            intent = query_analysis.get('intent', 'general')
            prompt_template = self.prompt_template.get_template(intent)
            
            # Fill prompt
            formatted_prompt = prompt_template.format(
                context=context,
                query=query
            )
            
            # Extract images for multimodal queries
            images = []
            if query_analysis.get('is_visual_query', False):
                images = self.extract_images_from_results(search_results)
            
            # Generate response
            if images and hasattr(self.llm_provider, 'generate_multimodal_response'):
                response_text = self.llm_provider.generate_multimodal_response(
                    formatted_prompt, 
                    images
                )
            else:
                response_text = self.llm_provider.generate_response(formatted_prompt)
            
            # Prepare response metadata
            sources = []
            for result in search_results[:5]:
                source = {
                    'id': result.id,
                    'title': result.metadata.get('title') or result.metadata.get('filename', 'Unknown'),
                    'type': result.metadata.get('source_type', 'unknown'),
                    'url': result.metadata.get('url') or result.metadata.get('file_url'),
                    'score': result.score,
                    'snippet': result.highlighted_text or result.text[:200] + "..."
                }
                sources.append(source)
            
            response = {
                'answer': response_text,
                'query': query,
                'intent': intent,
                'sources': sources,
                'total_sources': len(search_results),
                'has_visual_content': len(images) > 0,
                'query_analysis': query_analysis
            }
            
            logger.info(f"Generated response for query: {query[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'answer': "I apologize, but I encountered an error while generating a response to your question.",
                'query': query,
                'error': str(e),
                'sources': [],
                'total_sources': 0
            }

class RAGPipeline:
    """Complete RAG pipeline coordinating search and generation."""
    
    def __init__(self, 
                 search_engine, 
                 llm_provider_type: str = "openai",
                 **llm_kwargs):
        """
        Initialize RAG pipeline.
        
        Args:
            search_engine: HybridSearchEngine instance
            llm_provider_type: Type of LLM provider
            **llm_kwargs: Additional arguments for LLM provider
        """
        self.search_engine = search_engine
        
        # Initialize LLM provider
        if llm_provider_type == "openai":
            self.llm_provider = OpenAIProvider(**llm_kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider_type}")
        
        self.response_generator = ResponseGenerator(self.llm_provider)
        
        logger.info(f"Initialized RAG pipeline with {llm_provider_type} provider")
    
    def query(self, user_query: str, n_results: int = 10) -> Dict[str, Any]:
        """
        Process complete user query through RAG pipeline.
        
        Args:
            user_query: User's question
            n_results: Number of search results to consider
            
        Returns:
            Complete response with answer and sources
        """
        try:
            logger.info(f"Processing RAG query: {user_query}")
            
            # Perform search
            search_response = self.search_engine.search(user_query, n_results)
            
            if not search_response.get('results'):
                return {
                    'answer': "I couldn't find any relevant information in the Canvas materials to answer your question. Could you try rephrasing or asking about a different topic?",
                    'query': user_query,
                    'sources': [],
                    'total_sources': 0,
                    'search_results': search_response
                }
            
            # Generate response
            response = self.response_generator.generate_response(
                user_query,
                search_response['results'],
                search_response['query_analysis']
            )
            
            # Add search metadata
            response['search_results'] = search_response
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return {
                'answer': "I apologize, but I encountered an error while processing your question.",
                'query': user_query,
                'error': str(e),
                'sources': [],
                'total_sources': 0
            }
