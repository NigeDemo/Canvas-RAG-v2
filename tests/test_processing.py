"""Tests for content processing module."""

import sys
from pathlib import Path

import pytest
from unittest.mock import Mock, patch

# Ensure project root is importable when tests run directly
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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

    def test_extract_html_content_deduplicates_images(self):
        """Images with identical sources should be consolidated."""
        processor = ContentProcessor()

        html_content = """
        <p>Example</p>
        <img src="https://canvas.example.com/files/dup/preview" alt="Primary caption" />
        <img src="https://canvas.example.com/files/dup/preview" alt="Secondary caption" title="Alt title" />
        """

        result = processor.extract_html_content(html_content)

        assert len(result["image_urls"]) == 1
        image_entry = result["image_urls"][0]
        assert image_entry["src"] == "https://canvas.example.com/files/dup/preview"
        assert "Primary caption" in image_entry["alt"]
        assert "Secondary caption" in image_entry["alt"]
        assert "Alt title" in image_entry["title"]
    
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

    def test_process_content_item_page_with_parent_module(self, sample_canvas_page):
        """Page processing should inherit parent module context when provided."""
        processor = ContentProcessor()

        segments = processor.process_content_item(sample_canvas_page, parent_module="Session 5")

        text_chunks = [s for s in segments if s["content_type"] == "text_chunk"]
        image_refs = [s for s in segments if s["content_type"] == "image_reference"]

        assert text_chunks
        assert all(chunk.get("parent_module") == "Session 5" for chunk in text_chunks)
        assert image_refs
        assert all(ref.get("parent_module") == "Session 5" for ref in image_refs)
    
    @patch('PIL.Image.open')
    def test_process_image(self, mock_image_open):
        """Test image processing."""
        # Mock PIL Image
        mock_image = Mock()
        mock_image.mode = 'RGB'
        mock_image.width = 1000
        mock_image.height = 800
        mock_image.size = (1000, 800)
        mock_image.resize.return_value = mock_image
        mock_image_open.return_value.__enter__.return_value = mock_image
        
        processor = ContentProcessor(enable_vision=False)
        
        # Mock the image_to_base64 method
        with patch.object(processor, 'image_to_base64', return_value="fake_base64"):
            result = processor.process_image(Path("test_image.jpg"))
        
        assert result is not None
        assert result["content_type"] == "image"
        assert result["filename"] == "test_image.jpg"
        assert "image_base64" in result
