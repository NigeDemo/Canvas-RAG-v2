"""OCR processor for extracting text from architectural drawings."""

from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import re
from datetime import datetime

from .vision_processor import VisionProcessor
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

class OCRProcessor:
    """Specialized OCR processor for architectural drawings."""
    
    def __init__(self, vision_processor: VisionProcessor = None):
        """
        Initialize OCR processor.
        
        Args:
            vision_processor: Vision processor instance
        """
        self.vision_processor = vision_processor or VisionProcessor()
        
        # Architectural text patterns
        self.dimension_patterns = [
            r'\d+[\'"]\s*-?\s*\d*[\'"]*',  # Feet and inches
            r'\d+\.\d+\s*m',               # Meters
            r'\d+\s*mm',                   # Millimeters
            r'\d+\s*cm',                   # Centimeters
            r'\d+\s*ft',                   # Feet
            r'\d+\s*in',                   # Inches
            r'\d+\s*×\s*\d+',              # Dimensions (e.g., 10×20)
            r'\d+\s*x\s*\d+',              # Dimensions (e.g., 10x20)
        ]
        
        # Room and space patterns
        self.room_patterns = [
            r'\b(LIVING|DINING|KITCHEN|BEDROOM|BATHROOM|TOILET|OFFICE|STUDY)\b',
            r'\b(GARAGE|STORAGE|UTILITY|LAUNDRY|PANTRY|CLOSET|HALL|ENTRY)\b',
            r'\b(ROOM|SPACE|AREA|ZONE)\b',
            r'\bRM\s*\d+\b',  # Room numbers
        ]
        
        # Scale patterns
        self.scale_patterns = [
            r'1:\d+',                    # 1:100 format
            r'\d+[\'"]\s*=\s*\d+[\'-]+', # 1/4" = 1'-0" format
            r'SCALE\s*:\s*.*',           # Scale: notation
            r'N\.T\.S\.?',               # Not to scale
        ]
        
        # Technical specification patterns
        self.spec_patterns = [
            r'\b\d+\s*[xX]\s*\d+\s*[xX]\s*\d+\b',  # Lumber dimensions
            r'\b\d+\s*ga\b',                        # Gauge
            r'\b\d+\s*#\b',                         # Rebar numbers
            r'\bf\'?c\b',                           # On center
            r'\b[A-Z]{2,}\s*\d+\b',                 # Code references
        ]
    
    def extract_text(self, image_input: Union[str, bytes, Path]) -> str:
        """
        Extract all text from architectural drawing.
        
        Args:
            image_input: Image data
            
        Returns:
            Extracted text
        """
        return self.vision_processor.extract_text(image_input)
    
    def extract_structured_text(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Extract and categorize text from architectural drawing.
        
        Args:
            image_input: Image data
            
        Returns:
            Structured text extraction results
        """
        logger.info("Extracting structured text from architectural drawing")
        
        # Get raw text
        raw_text = self.extract_text(image_input)
        
        if not raw_text:
            return {
                "success": False,
                "error": "No text extracted",
                "timestamp": datetime.now().isoformat()
            }
        
        # Categorize extracted text
        result = {
            "raw_text": raw_text,
            "dimensions": self._extract_dimensions(raw_text),
            "room_labels": self._extract_room_labels(raw_text),
            "scale_info": self._extract_scale_info(raw_text),
            "technical_specs": self._extract_technical_specs(raw_text),
            "title_block": self._extract_title_block(raw_text),
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def _extract_dimensions(self, text: str) -> List[str]:
        """Extract dimensional information from text."""
        dimensions = []
        
        for pattern in self.dimension_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dimensions.extend(matches)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(dimensions))
    
    def _extract_room_labels(self, text: str) -> List[str]:
        """Extract room and space labels from text."""
        room_labels = []
        
        for pattern in self.room_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            room_labels.extend(matches)
        
        # Also look for capitalized words that might be room names
        capitalized_words = re.findall(r'\b[A-Z][A-Z\s]+\b', text)
        room_labels.extend([word.strip() for word in capitalized_words if len(word.strip()) > 2])
        
        return list(dict.fromkeys(room_labels))
    
    def _extract_scale_info(self, text: str) -> List[str]:
        """Extract scale information from text."""
        scale_info = []
        
        for pattern in self.scale_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            scale_info.extend(matches)
        
        return list(dict.fromkeys(scale_info))
    
    def _extract_technical_specs(self, text: str) -> List[str]:
        """Extract technical specifications from text."""
        specs = []
        
        for pattern in self.spec_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            specs.extend(matches)
        
        return list(dict.fromkeys(specs))
    
    def _extract_title_block(self, text: str) -> Dict[str, Any]:
        """Extract title block information from text."""
        title_block = {}
        
        # Look for common title block fields
        patterns = {
            'project_name': r'PROJECT\s*:?\s*(.+?)(?:\n|$)',
            'drawing_title': r'TITLE\s*:?\s*(.+?)(?:\n|$)',
            'scale': r'SCALE\s*:?\s*(.+?)(?:\n|$)',
            'date': r'DATE\s*:?\s*(.+?)(?:\n|$)',
            'drawn_by': r'DRAWN\s*BY\s*:?\s*(.+?)(?:\n|$)',
            'checked_by': r'CHECKED\s*BY\s*:?\s*(.+?)(?:\n|$)',
            'drawing_number': r'DWG\s*NO\s*:?\s*(.+?)(?:\n|$)',
            'sheet_number': r'SHEET\s*:?\s*(.+?)(?:\n|$)',
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                title_block[field] = match.group(1).strip()
        
        return title_block
    
    def extract_dimensions_with_context(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Extract dimensions with surrounding context.
        
        Args:
            image_input: Image data
            
        Returns:
            Dimensions with context
        """
        dimension_prompt = """Extract all dimensions and measurements from this architectural drawing. For each dimension, provide:
1. The numerical value and unit
2. What element or space it's measuring
3. The location or context within the drawing
4. Whether it's a primary dimension or a secondary measurement

Format your response as a structured list with clear identification of each dimension."""
        
        result = self.vision_processor.analyze_image(image_input, dimension_prompt)
        
        return {
            "analysis_type": "dimensions_with_context",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def extract_room_schedule(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Extract room schedule information if present.
        
        Args:
            image_input: Image data
            
        Returns:
            Room schedule information
        """
        schedule_prompt = """Look for any room schedule, door schedule, or window schedule in this drawing. Extract:
1. Room numbers and names
2. Room areas/square footage
3. Finish schedules
4. Door types and hardware
5. Window types and sizes
6. Any other schedule information

Present the information in a clear, organized format."""
        
        result = self.vision_processor.analyze_image(image_input, schedule_prompt)
        
        return {
            "analysis_type": "room_schedule",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def extract_specifications(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Extract technical specifications and notes.
        
        Args:
            image_input: Image data
            
        Returns:
            Technical specifications
        """
        specs_prompt = """Extract all technical specifications, construction notes, and material callouts from this drawing. Include:
1. Material specifications
2. Construction details and notes
3. Code references
4. Structural requirements
5. Finish specifications
6. Any other technical information

Organize the information by category and provide clear descriptions."""
        
        result = self.vision_processor.analyze_image(image_input, specs_prompt)
        
        return {
            "analysis_type": "specifications",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def comprehensive_text_extraction(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Perform comprehensive text extraction and analysis.
        
        Args:
            image_input: Image data
            
        Returns:
            Complete text extraction results
        """
        logger.info("Starting comprehensive text extraction")
        
        # Basic structured extraction
        structured_result = self.extract_structured_text(image_input)
        
        if not structured_result.get("success"):
            return structured_result
        
        # Enhanced extractions
        try:
            dimensions_result = self.extract_dimensions_with_context(image_input)
            schedule_result = self.extract_room_schedule(image_input)
            specs_result = self.extract_specifications(image_input)
            
            return {
                "basic_extraction": structured_result,
                "dimensions_with_context": dimensions_result,
                "room_schedule": schedule_result,
                "specifications": specs_result,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive text extraction: {e}")
            return {
                "basic_extraction": structured_result,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_extraction(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and score extraction results.
        
        Args:
            extraction_result: Text extraction results
            
        Returns:
            Validation results
        """
        if not extraction_result.get("success"):
            return {"validation_score": 0, "issues": ["Extraction failed"]}
        
        issues = []
        score = 0
        
        # Check for basic elements
        if extraction_result.get("raw_text"):
            score += 20
        else:
            issues.append("No raw text extracted")
        
        if extraction_result.get("dimensions"):
            score += 20
        else:
            issues.append("No dimensions found")
        
        if extraction_result.get("room_labels"):
            score += 20
        else:
            issues.append("No room labels found")
        
        if extraction_result.get("scale_info"):
            score += 20
        else:
            issues.append("No scale information found")
        
        if extraction_result.get("title_block"):
            score += 20
        else:
            issues.append("No title block information found")
        
        return {
            "validation_score": score,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }
