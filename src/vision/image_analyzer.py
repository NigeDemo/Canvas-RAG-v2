"""Image analyzer for architectural drawings with specialized analysis capabilities."""

from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import json
from datetime import datetime

from .vision_processor import VisionProcessor
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ArchitecturalDrawingAnalyzer:
    """Specialized analyzer for architectural drawings."""
    
    def __init__(self, vision_processor: VisionProcessor = None):
        """
        Initialize architectural drawing analyzer.
        
        Args:
            vision_processor: Vision processor instance
        """
        self.vision_processor = vision_processor or VisionProcessor()
        
        # Architecture-specific analysis prompts
        self.analysis_prompts = {
            "drawing_type": """Identify the type of architectural drawing shown. Common types include:
- Floor plan
- Site plan
- Elevation (front, side, rear)
- Section (cross-section, longitudinal)
- Detail drawing
- Perspective or 3D view
- Isometric or axonometric
- Reflected ceiling plan
- Structural plan

Provide the drawing type and explain your reasoning.""",
            
            "scale_analysis": """Analyze the scale and dimensional information in this drawing:
1. What scale is indicated (e.g., 1:100, 1/4" = 1'-0")?
2. Are there dimension lines and measurements visible?
3. What are the key measurements shown?
4. Is there a scale bar or reference?
5. Are the proportions consistent with the stated scale?""",
            
            "spatial_analysis": """Analyze the spatial organization and layout:
1. What rooms or spaces are shown?
2. How are the spaces connected?
3. What is the circulation pattern?
4. Are there specific architectural elements (stairs, doors, windows)?
5. What is the overall spatial relationship?""",
            
            "technical_elements": """Identify technical elements and construction details:
1. What construction materials are indicated?
2. Are there hatching patterns or symbols?
3. What structural elements are shown?
4. Are there technical specifications or notes?
5. What drafting conventions are used?""",
            
            "annotation_analysis": """Analyze all text, annotations, and labels:
1. Extract all visible text and dimensions
2. Identify room labels and identifiers
3. List technical specifications
4. Note any title block information
5. Identify scale indicators and legends"""
        }
        
        # Question-specific prompts for different query types
        self.query_prompts = {
            "what_is_shown": "What architectural elements and features are visible in this drawing?",
            "measurements": "What are the key measurements and dimensions shown in this drawing?",
            "materials": "What construction materials and finishes are indicated in this drawing?",
            "spaces": "What rooms or spaces are shown and how are they organized?",
            "technical_specs": "What technical specifications and construction details are provided?",
            "symbols": "What architectural symbols, hatching patterns, or notations are used?"
        }
    
    def analyze_drawing_type(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Determine the type of architectural drawing.
        
        Args:
            image_input: Image data
            
        Returns:
            Drawing type analysis
        """
        result = self.vision_processor.analyze_image(
            image_input, 
            self.analysis_prompts["drawing_type"]
        )
        
        return {
            "analysis_type": "drawing_type",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_scale_and_dimensions(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Analyze scale and dimensional information.
        
        Args:
            image_input: Image data
            
        Returns:
            Scale analysis
        """
        result = self.vision_processor.analyze_image(
            image_input,
            self.analysis_prompts["scale_analysis"]
        )
        
        return {
            "analysis_type": "scale_analysis",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_spatial_organization(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Analyze spatial organization and layout.
        
        Args:
            image_input: Image data
            
        Returns:
            Spatial analysis
        """
        result = self.vision_processor.analyze_image(
            image_input,
            self.analysis_prompts["spatial_analysis"]
        )
        
        return {
            "analysis_type": "spatial_analysis",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_technical_elements(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Analyze technical elements and construction details.
        
        Args:
            image_input: Image data
            
        Returns:
            Technical analysis
        """
        result = self.vision_processor.analyze_image(
            image_input,
            self.analysis_prompts["technical_elements"]
        )
        
        return {
            "analysis_type": "technical_elements",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def extract_annotations(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Extract all annotations and text from the drawing.
        
        Args:
            image_input: Image data
            
        Returns:
            Annotation analysis
        """
        result = self.vision_processor.analyze_image(
            image_input,
            self.analysis_prompts["annotation_analysis"]
        )
        
        return {
            "analysis_type": "annotation_analysis",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def comprehensive_analysis(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of architectural drawing.
        
        Args:
            image_input: Image data
            
        Returns:
            Complete analysis results
        """
        logger.info("Starting comprehensive architectural drawing analysis")
        
        analyses = {}
        
        # Run all analysis types
        for analysis_type, prompt in self.analysis_prompts.items():
            try:
                result = self.vision_processor.analyze_image(image_input, prompt)
                analyses[analysis_type] = {
                    "result": result,
                    "success": result.get("success", False)
                }
            except Exception as e:
                logger.error(f"Error in {analysis_type} analysis: {e}")
                analyses[analysis_type] = {
                    "result": {"error": str(e), "success": False},
                    "success": False
                }
        
        # Summary
        successful_analyses = [k for k, v in analyses.items() if v["success"]]
        
        return {
            "analysis_type": "comprehensive",
            "analyses": analyses,
            "successful_analyses": successful_analyses,
            "total_analyses": len(self.analysis_prompts),
            "success_rate": len(successful_analyses) / len(self.analysis_prompts),
            "timestamp": datetime.now().isoformat()
        }
    
    def query_specific_analysis(self, 
                              image_input: Union[str, bytes, Path], 
                              query: str) -> Dict[str, Any]:
        """
        Perform analysis tailored to specific query.
        
        Args:
            image_input: Image data
            query: User query about the drawing
            
        Returns:
            Query-specific analysis
        """
        # Determine query type and create appropriate prompt
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["what", "show", "element", "feature"]):
            prompt = self.query_prompts["what_is_shown"]
        elif any(word in query_lower for word in ["measure", "dimension", "size", "scale"]):
            prompt = self.query_prompts["measurements"]
        elif any(word in query_lower for word in ["material", "construction", "finish"]):
            prompt = self.query_prompts["materials"]
        elif any(word in query_lower for word in ["room", "space", "layout", "organization"]):
            prompt = self.query_prompts["spaces"]
        elif any(word in query_lower for word in ["technical", "specification", "detail"]):
            prompt = self.query_prompts["technical_specs"]
        elif any(word in query_lower for word in ["symbol", "notation", "hatch", "pattern"]):
            prompt = self.query_prompts["symbols"]
        else:
            # Generic architectural analysis
            prompt = f"Analyze this architectural drawing to answer: {query}"
        
        result = self.vision_processor.analyze_image(image_input, prompt)
        
        return {
            "analysis_type": "query_specific",
            "query": query,
            "prompt_used": prompt,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

class ImageAnalyzer:
    """Main image analyzer coordinating different analysis types."""
    
    def __init__(self, vision_processor: VisionProcessor = None):
        """
        Initialize image analyzer.
        
        Args:
            vision_processor: Vision processor instance
        """
        self.vision_processor = vision_processor or VisionProcessor()
        self.architectural_analyzer = ArchitecturalDrawingAnalyzer(self.vision_processor)
        
        logger.info("Initialized ImageAnalyzer")
    
    def analyze_image(self, 
                     image_input: Union[str, bytes, Path],
                     analysis_type: str = "comprehensive",
                     query: str = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Analyze image based on type and query.
        
        Args:
            image_input: Image data
            analysis_type: Type of analysis to perform
            query: Specific user query
            **kwargs: Additional parameters
            
        Returns:
            Analysis results
        """
        try:
            if analysis_type == "comprehensive":
                return self.architectural_analyzer.comprehensive_analysis(image_input)
            elif analysis_type == "drawing_type":
                return self.architectural_analyzer.analyze_drawing_type(image_input)
            elif analysis_type == "scale":
                return self.architectural_analyzer.analyze_scale_and_dimensions(image_input)
            elif analysis_type == "spatial":
                return self.architectural_analyzer.analyze_spatial_organization(image_input)
            elif analysis_type == "technical":
                return self.architectural_analyzer.analyze_technical_elements(image_input)
            elif analysis_type == "annotations":
                return self.architectural_analyzer.extract_annotations(image_input)
            elif analysis_type == "query_specific" and query:
                return self.architectural_analyzer.query_specific_analysis(image_input, query)
            elif analysis_type == "description":
                description = self.vision_processor.describe_image(image_input)
                return {
                    "analysis_type": "description",
                    "description": description,
                    "timestamp": datetime.now().isoformat()
                }
            elif analysis_type == "ocr":
                extracted_text = self.vision_processor.extract_text(image_input)
                return {
                    "analysis_type": "ocr",
                    "extracted_text": extracted_text,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            return {
                "analysis_type": analysis_type,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def batch_analyze_images(self, 
                           image_inputs: List[Union[str, bytes, Path]],
                           analysis_type: str = "comprehensive",
                           **kwargs) -> List[Dict[str, Any]]:
        """
        Analyze multiple images with the same analysis type.
        
        Args:
            image_inputs: List of image data
            analysis_type: Type of analysis to perform
            **kwargs: Additional parameters
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i, image_input in enumerate(image_inputs):
            logger.info(f"Analyzing image {i+1}/{len(image_inputs)}")
            result = self.analyze_image(image_input, analysis_type, **kwargs)
            results.append(result)
        
        return results
    
    def get_analysis_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of analysis results.
        
        Args:
            results: List of analysis results
            
        Returns:
            Summary statistics
        """
        if not results:
            return {"total": 0, "successful": 0, "failed": 0}
        
        successful = sum(1 for r in results if r.get("success", True))
        failed = len(results) - successful
        
        analysis_types = [r.get("analysis_type") for r in results]
        
        return {
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(results) if results else 0,
            "analysis_types": list(set(analysis_types)),
            "timestamp": datetime.now().isoformat()
        }
