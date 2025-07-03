#!/usr/bin/env python3
"""Debug script to test the indexing process."""

import json
from src.indexing import IndexBuilder

# Load processed content
with open('data/processed/processed_page_construction_drawing_package_2_metadata.json', 'r', encoding='utf-8') as f:
    content_segments = json.load(f)

print(f"Total segments: {len(content_segments)}")

# Count types
text_chunks = [s for s in content_segments if s.get("content_type") == "text_chunk"]
image_refs = [s for s in content_segments if s.get("content_type") == "image_reference"]

print(f"Text chunks: {len(text_chunks)}")
print(f"Image references: {len(image_refs)}")

# Simulate the indexing logic
documents = []
metadata = []
content_for_embedding = []

for segment in content_segments:
    # Extract document text
    doc_text = ""
    if "text" in segment and segment["text"]:
        doc_text = segment["text"]
    elif segment.get("content_type") == "image_reference":
        doc_text = f"[Image: {segment.get('alt_text', 'architectural drawing')}]"
    
    if doc_text:
        documents.append(doc_text)
        metadata.append(segment)
        content_for_embedding.append(segment)

print(f"Documents to be indexed: {len(documents)}")

# Show breakdown
text_docs = [i for i, seg in enumerate(content_for_embedding) if seg.get("content_type") == "text_chunk"]
image_docs = [i for i, seg in enumerate(content_for_embedding) if seg.get("content_type") == "image_reference"]

print(f"Text documents: {len(text_docs)}")
print(f"Image documents: {len(image_docs)}")

# Show a few examples
print("\nFirst 3 image documents:")
for i, doc_idx in enumerate(image_docs[:3]):
    print(f"  {i+1}. {documents[doc_idx]}")
    print(f"     Alt text: {content_for_embedding[doc_idx].get('alt_text', 'N/A')}")
    print(f"     Image URL: {content_for_embedding[doc_idx].get('image_url', 'N/A')}")
    print()
