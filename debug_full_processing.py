#!/usr/bin/env python3
"""Debug script to test the full content processing."""

import json
from src.processing.content_processor import ContentProcessor

# Load the raw HTML content
with open('data/raw/page_construction_drawing_package_2_metadata.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# Test full content processing for the page
processor = ContentProcessor()
page_item = raw_data["page"]
page_item["type"] = "page"  # Add the required type field

processed_segments = processor.process_content_item(page_item)

print(f"Total processed segments: {len(processed_segments)}")

# Count different types
text_chunks = [s for s in processed_segments if s.get("content_type") == "text_chunk"]
image_refs = [s for s in processed_segments if s.get("content_type") == "image_reference"]

print(f"Text chunks: {len(text_chunks)}")
print(f"Image references: {len(image_refs)}")

# Show first few image references
if image_refs:
    print("\nFirst 3 image references:")
    for i, img_ref in enumerate(image_refs[:3]):
        print(f"  {i+1}. URL: {img_ref.get('image_url')}")
        print(f"     Alt: {img_ref.get('alt_text')}")
        print()
else:
    print("\nNo image references found!")
