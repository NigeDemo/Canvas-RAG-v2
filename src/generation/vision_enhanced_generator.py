"""Enhanced multimodal response generator with vision AI integration."""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import json
from datetime import datetime

from ..vision.vision_processor import VisionProcessor
from ..vision.image_analyzer import ImageAnalyzer
from ..generation.llm_integration import ResponseGenerator, PromptTemplate
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class VisionEnhancedContext:
    """Enhanced context with vision analysis results."""
    text_context: str
    image_references: List[Dict[str, Any]]
    vision_analyses: List[Dict[str, Any]]
    query_type: str
    analysis_summary: str

class VisionEnhancedResponseGenerator(ResponseGenerator):
    """Response generator with vision AI capabilities."""
    
    def __init__(self, llm_provider=None, vision_processor=None):
        """
        Initialize vision-enhanced response generator.
        
        Args:
            llm_provider: LLM provider instance
            vision_processor: Vision processor instance
        """
        # Initialize LLM provider if not provided
        if llm_provider is None:
            try:
                from ..generation.llm_integration import OpenAIProvider
                llm_provider = OpenAIProvider()
            except Exception as e:
                logger.error(f"Failed to initialize default LLM provider: {e}")
                # Create a dummy provider that returns error messages
                llm_provider = self._create_dummy_provider()
        
        super().__init__(llm_provider)
        self.vision_processor = vision_processor or VisionProcessor()
        self.image_analyzer = ImageAnalyzer(self.vision_processor)
        
        # Vision-enhanced prompt templates
        self.vision_templates = {
            'vision_analysis': """You are an expert architectural drawing analyst helping students understand visual content in technical drawings.

Context: The following content was retrieved from Canvas course materials:

Text Content:
{text_context}

Visual Analysis Results:
{vision_analyses}

Available Images:
{image_references}

Student Question: {query}

Instructions:
- Use the visual analysis results to provide detailed insights about the architectural drawings
- Reference specific visual elements identified in the analysis
- Explain technical aspects using the OCR and dimensional information extracted
- Provide clickable links to images: [Image Description](URL)
- Connect visual elements to architectural principles and standards
- If you can identify specific drawing types, scales, or technical details, mention them
- Focus on educational value for architecture students

Answer:""",

            'measurement_analysis': """You are an expert in architectural dimensioning and scale analysis helping students understand technical drawings.

Context: The following content was retrieved from Canvas course materials:

Text Content:
{text_context}

Dimensional Analysis:
{dimension_analysis}

Scale Information:
{scale_info}

Available Images:
{image_references}

Student Question: {query}

Instructions:
- Focus on dimensional accuracy and scale relationships
- Explain how measurements relate to real-world construction
- Reference specific dimensions found in the visual analysis
- Discuss scale implications for design and construction
- Provide practical guidance for reading architectural drawings
- Include relevant Canvas links and image references

Answer:""",

            'spatial_analysis': """You are an expert in architectural spatial organization helping students understand layout and design principles.

Context: The following content was retrieved from Canvas course materials:

Text Content:
{text_context}

Spatial Analysis:
{spatial_analysis}

Room Organization:
{room_analysis}

Available Images:
{image_references}

Student Question: {query}

Instructions:
- Analyze spatial relationships and circulation patterns
- Explain how rooms and spaces connect and function
- Reference specific spatial elements identified in the analysis
- Discuss design principles affecting spatial organization
- Provide insights into architectural planning strategies
- Include relevant Canvas links and image references

Answer:""",

            'technical_analysis': """You are an expert in construction technology helping students understand technical specifications and details.

Context: The following content was retrieved from Canvas course materials:

Text Content:
{text_context}

Technical Analysis:
{technical_analysis}

Construction Details:
{construction_details}

Available Images:
{image_references}

Student Question: {query}

Instructions:
- Focus on construction methods and material specifications
- Explain technical details and their real-world applications
- Reference specific construction elements identified in the analysis
- Discuss building codes and standards where relevant
- Provide practical guidance for construction document interpretation
- Include relevant Canvas links and image references

Answer:"""
        }
        
        logger.info("Initialized VisionEnhancedResponseGenerator")
    
    def analyze_images_for_query(self, 
                                image_references: List[Dict[str, Any]], 
                                query: str,
                                query_type: str) -> List[Dict[str, Any]]:
        """
        Analyze images based on query type and content.
        
        Args:
            image_references: List of image reference dictionaries
            query: User query
            query_type: Type of query (spatial, technical, measurement, etc.)
            
        Returns:
            List of vision analysis results
        """
        if not image_references:
            return []
        
        analyses = []
        
        # Determine analysis type based on query
        if query_type == "measurement" or any(word in query.lower() for word in ["dimension", "scale", "size", "measure"]):
            analysis_type = "scale"
        elif query_type == "spatial" or any(word in query.lower() for word in ["room", "space", "layout", "organization"]):
            analysis_type = "spatial"
        elif query_type == "technical" or any(word in query.lower() for word in ["construction", "detail", "material", "specification"]):
            analysis_type = "technical"
        else:
            analysis_type = "query_specific"
        
        # Analyze each image
        for img_ref in image_references[:3]:  # Limit to 3 images to avoid token limits
            try:
                image_url = img_ref.get("image_url")
                if not image_url:
                    continue
                
                logger.info(f"Analyzing image: {img_ref.get('alt_text', 'Unknown')}")
                
                if analysis_type == "query_specific":
                    analysis = self.image_analyzer.analyze_image(
                        image_url, 
                        analysis_type=analysis_type,
                        query=query
                    )
                else:
                    analysis = self.image_analyzer.analyze_image(
                        image_url, 
                        analysis_type=analysis_type
                    )
                
                analysis["image_reference"] = img_ref
                analyses.append(analysis)
                
            except Exception as e:
                logger.error(f"Error analyzing image {img_ref.get('alt_text', 'Unknown')}: {e}")
                continue
        
        return analyses
    
    def create_vision_enhanced_context(self, 
                                     text_context: str,
                                     image_references: List[Dict[str, Any]],
                                     query: str,
                                     query_type: str) -> VisionEnhancedContext:
        """
        Create enhanced context with vision analysis.
        
        Args:
            text_context: Text context from retrieval
            image_references: Image references from retrieval
            query: User query
            query_type: Type of query
            
        Returns:
            Enhanced context with vision analysis
        """
        # Analyze images if available
        vision_analyses = []
        if image_references:
            vision_analyses = self.analyze_images_for_query(image_references, query, query_type)
        
        # Create analysis summary
        analysis_summary = self._create_analysis_summary(vision_analyses)
        
        return VisionEnhancedContext(
            text_context=text_context,
            image_references=image_references,
            vision_analyses=vision_analyses,
            query_type=query_type,
            analysis_summary=analysis_summary
        )
    
    def _create_analysis_summary(self, vision_analyses: List[Dict[str, Any]]) -> str:
        """Create a summary of vision analysis results."""
        if not vision_analyses:
            return "No visual analysis performed."
        
        summary_parts = []
        
        for i, analysis in enumerate(vision_analyses, 1):
            analysis_type = analysis.get("analysis_type", "unknown")
            success = analysis.get("success", False) or analysis.get("result", {}).get("success", False)
            
            if success:
                summary_parts.append(f"Image {i}: {analysis_type} analysis completed successfully")
            else:
                summary_parts.append(f"Image {i}: {analysis_type} analysis failed")
        
        return "; ".join(summary_parts)
    
    def generate_vision_enhanced_response(self, 
                                        enhanced_context: VisionEnhancedContext,
                                        query: str) -> str:
        """
        Generate response using vision-enhanced context.
        
        Args:
            enhanced_context: Enhanced context with vision analysis
            query: User query
            
        Returns:
            Generated response
        """
        try:
            # Determine appropriate template
            query_type = enhanced_context.query_type
            
            if query_type == "measurement":
                template_name = "measurement_analysis"
            elif query_type == "spatial":
                template_name = "spatial_analysis"
            elif query_type == "technical":
                template_name = "technical_analysis"
            else:
                template_name = "vision_analysis"
            
            # Prepare template variables
            template_vars = {
                "text_context": enhanced_context.text_context,
                "query": query,
                "image_references": self._format_image_references(enhanced_context.image_references),
                "vision_analyses": self._format_vision_analyses(enhanced_context.vision_analyses)
            }
            
            # Add specific analysis results based on template
            if template_name == "measurement_analysis":
                template_vars.update({
                    "dimension_analysis": self._extract_dimensional_info(enhanced_context.vision_analyses),
                    "scale_info": self._extract_scale_info(enhanced_context.vision_analyses)
                })
            elif template_name == "spatial_analysis":
                template_vars.update({
                    "spatial_analysis": self._extract_spatial_info(enhanced_context.vision_analyses),
                    "room_analysis": self._extract_room_info(enhanced_context.vision_analyses)
                })
            elif template_name == "technical_analysis":
                template_vars.update({
                    "technical_analysis": self._extract_technical_info(enhanced_context.vision_analyses),
                    "construction_details": self._extract_construction_details(enhanced_context.vision_analyses)
                })
            
            # Generate response
            prompt = self.vision_templates[template_name].format(**template_vars)
            response = self.llm_provider.generate_response(prompt)
            
            # Add metadata
            response_metadata = {
                "template_used": template_name,
                "images_analyzed": len(enhanced_context.vision_analyses),
                "analysis_summary": enhanced_context.analysis_summary,
                "timestamp": datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating vision-enhanced response: {e}")
            return "I apologize, but I encountered an error processing the visual content and generating a response."
    
    def _format_image_references(self, image_references: List[Dict[str, Any]]) -> str:
        """Format image references for prompt."""
        if not image_references:
            return "No images available."
        
        formatted = []
        for i, img_ref in enumerate(image_references, 1):
            alt_text = img_ref.get("alt_text", "Unknown")
            url = img_ref.get("image_url", "#")
            formatted.append(f"{i}. [{alt_text}]({url})")
        
        return "\n".join(formatted)
    
    def _format_vision_analyses(self, vision_analyses: List[Dict[str, Any]]) -> str:
        """Format vision analysis results for prompt."""
        if not vision_analyses:
            return "No visual analysis performed."
        
        formatted = []
        for i, analysis in enumerate(vision_analyses, 1):
            analysis_type = analysis.get("analysis_type", "unknown")
            result = analysis.get("result", {})
            
            if result.get("success"):
                content = result.get("analysis", "No analysis content")
                formatted.append(f"Image {i} ({analysis_type}):\n{content}")
            else:
                error = result.get("error", "Analysis failed")
                formatted.append(f"Image {i} ({analysis_type}): Failed - {error}")
        
        return "\n\n".join(formatted)
    
    def _extract_dimensional_info(self, vision_analyses: List[Dict[str, Any]]) -> str:
        """Extract dimensional information from vision analyses."""
        dimensional_info = []
        
        for analysis in vision_analyses:
            if analysis.get("analysis_type") == "scale":
                result = analysis.get("result", {})
                if result.get("success"):
                    dimensional_info.append(result.get("analysis", ""))
        
        return "\n".join(dimensional_info) if dimensional_info else "No dimensional information extracted."
    
    def _extract_scale_info(self, vision_analyses: List[Dict[str, Any]]) -> str:
        """Extract scale information from vision analyses."""
        # Similar implementation for scale info
        return "Scale information processing not yet implemented."
    
    def _extract_spatial_info(self, vision_analyses: List[Dict[str, Any]]) -> str:
        """Extract spatial information from vision analyses."""
        spatial_info = []
        
        for analysis in vision_analyses:
            if analysis.get("analysis_type") == "spatial":
                result = analysis.get("result", {})
                if result.get("success"):
                    spatial_info.append(result.get("analysis", ""))
        
        return "\n".join(spatial_info) if spatial_info else "No spatial information extracted."
    
    def _extract_room_info(self, vision_analyses: List[Dict[str, Any]]) -> str:
        """Extract room information from vision analyses."""
        # Similar implementation for room info
        return "Room information processing not yet implemented."
    
    def _extract_technical_info(self, vision_analyses: List[Dict[str, Any]]) -> str:
        """Extract technical information from vision analyses."""
        technical_info = []
        
        for analysis in vision_analyses:
            if analysis.get("analysis_type") == "technical":
                result = analysis.get("result", {})
                if result.get("success"):
                    technical_info.append(result.get("analysis", ""))
        
        return "\n".join(technical_info) if technical_info else "No technical information extracted."
    
    def _extract_construction_details(self, vision_analyses: List[Dict[str, Any]]) -> str:
        """Extract construction details from vision analyses."""
        # Similar implementation for construction details
        return "Construction details processing not yet implemented."
    
    def _create_dummy_provider(self):
        """Create a dummy LLM provider for fallback."""
        class DummyProvider:
            def generate_response(self, prompt: str, **kwargs) -> str:
                return "I apologize, but the LLM provider is not properly configured. Please check your API keys and configuration."
            
            def generate_multimodal_response(self, prompt: str, images: List[str] = None, **kwargs) -> str:
                return "I apologize, but the LLM provider is not properly configured. Please check your API keys and configuration."
        
        return DummyProvider()
