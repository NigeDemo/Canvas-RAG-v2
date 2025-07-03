"""Tests for content processing module."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.processing.content_processor import ContentProcessor

class TestContentProcessor:
    """Test cases for ContentProcessor."""
    
    def test_extract_html_content(self, sample_canvas_page):
        """Test HTML content extraction."""
        processor = ContentProcessor()
        
        html_content = sample_canvas_page["body"]
        result = processor.extract_html_content(html_content)
        
        assert result["content_type"] == "html"
        assert "Scale and Dimensioning" in result["text"]
        assert "Site plans: 1:500" in result["text"]
        assert len(result["image_urls"]) == 1
        assert result["image_urls"][0]["alt"] == "Example of proper dimensioning"
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        processor = ContentProcessor()
        
        text = "This is a test text. " * 100  # Create long text
        chunks = processor.chunk_text(text, {"source": "test"})
        
        assert len(chunks) > 1
        assert all("source" in chunk for chunk in chunks)
        assert all(chunk["content_type"] == "text_chunk" for chunk in chunks)
    
    def test_process_content_item_page(self, sample_canvas_page):
        """Test processing a Canvas page."""
        processor = ContentProcessor()
        
        segments = processor.process_content_item(sample_canvas_page)
        
        # Should have text chunks and image references
        text_chunks = [s for s in segments if s["content_type"] == "text_chunk"]
        image_refs = [s for s in segments if s["content_type"] == "image_reference"]
        
        assert len(text_chunks) > 0
        assert len(image_refs) == 1
        assert image_refs[0]["alt_text"] == "Example of proper dimensioning"
    
    @patch('PIL.Image.open')
    def test_process_image(self, mock_image_open):
        """Test image processing."""
        # Mock PIL Image
        mock_image = Mock()
        mock_image.mode = 'RGB'
        mock_image.width = 1000
        mock_image.height = 800
        mock_image.resize.return_value = mock_image
        mock_image_open.return_value.__enter__.return_value = mock_image
        
        processor = ContentProcessor()
        
        # Mock the image_to_base64 method
        with patch.object(processor, 'image_to_base64', return_value="fake_base64"):
            result = processor.process_image(Path("test_image.jpg"))
        
        assert result is not None
        assert result["content_type"] == "image"
        assert result["filename"] == "test_image.jpg"
        assert "image_base64" in result
