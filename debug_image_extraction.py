#!/usr/bin/env python3
"""Debug script to test image extraction from HTML content."""

import json
from src.processing.content_processor import ContentProcessor

# Load the raw HTML content (update filename to match your data)
with open('data/raw/page_construction_drawing_package_2_metadata.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

html_content = raw_data["page"]["body"]

# Test image extraction
processor = ContentProcessor()
extracted = processor.extract_html_content(html_content)

print(f"Extracted {len(extracted['image_urls'])} images:")
for i, img in enumerate(extracted['image_urls'][:5]):  # Show first 5
    print(f"  {i+1}. URL: {img['src']}")
    print(f"     Alt: {img['alt']}")
    print(f"     Title: {img['title']}")
    print()

print(f"Total text length: {len(extracted['text'])} characters")
print(f"First 200 characters of text: {extracted['text'][:200]}...")
