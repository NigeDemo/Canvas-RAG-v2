"""Test configuration and utilities."""

import pytest
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)

@pytest.fixture
def sample_canvas_page():
    """Sample Canvas page data for testing."""
    return {
        "id": "test_page_1",
        "title": "Architectural Drawing Basics",
        "url": "https://canvas.example.com/pages/drawing-basics",
        "body": """
        <h1>Scale and Dimensioning in Architectural Drawings</h1>
        <p>When creating architectural drawings, proper scale and dimensioning are crucial for accurate communication.</p>
        
        <h2>Common Scales</h2>
        <ul>
            <li>Site plans: 1:500 or 1:1000</li>
            <li>Floor plans: 1:100 or 1:50</li>
            <li>Sections: 1:100 or 1:50</li>
            <li>Details: 1:20, 1:10, or 1:5</li>
        </ul>
        
        <h2>Dimensioning Guidelines</h2>
        <p>Dimension lines should remain within the page margin and avoid overlapping hatching patterns.</p>
        
        <img src="https://canvas.example.com/files/123/preview" alt="Example of proper dimensioning" />
        """,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "published": True,
        "type": "page"
    }

@pytest.fixture
def sample_pdf_metadata():
    """Sample PDF file metadata for testing."""
    return {
        "id": "test_file_1",
        "filename": "drawing_standards.pdf",
        "path": "/test/path/drawing_standards.pdf",
        "url": "https://canvas.example.com/files/456/download",
        "content_type": "application/pdf",
        "size": 1024000,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "type": "file"
    }

@pytest.fixture
def sample_search_query():
    """Sample search queries for testing."""
    return {
        "factual": "What scale should I use for a floor plan?",
        "visual": "Show me examples of proper dimensioning in section drawings",
        "measurement": "What are the standard scales for architectural drawings?",
        "general": "How do I create technical drawings?"
    }
