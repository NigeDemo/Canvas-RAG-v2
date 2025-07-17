# Technical Implementation Notes

## Quick Context for New Contributors

**Project**: Canvas RAG v2 - Architecture course content assistant  
**Domain**: Architecture education, technical drawing analysis  
**Current Status**: Phase 2 complete (vision AI integration fully implemented)  
**Next Priority**: Performance optimization and BM25 integration (Phase 3)  
**Tech Stack**: Canvas API → Python → OpenAI (embeddings + GPT-4 + Vision) → ChromaDB → Streamlit  

---

## Current Architecture (Phase 2 Complete)

### Data Flow
1. **Canvas Ingestion**: Extract HTML pages and image references
2. **Content Processing**: Parse HTML, extract text and image URLs
3. **Vectorization**: Create embeddings using OpenAI text-embedding-3-large
4. **Storage**: Store in ChromaDB with metadata
5. **Retrieval**: Vector similarity search with image reference filtering
6. **Vision AI Integration**: GPT-4 Vision analysis for architectural drawings
7. **Generation**: GPT-4 synthesis with intelligent prompting and vision analysis

### What Gets Indexed

#### Text Chunks
```json
{
  "content_type": "text_chunk",
  "text": "Construction drawings form the essential instructions...",
  "chunk_index": 0,
  "source_id": 1440959,
  "title": "construction drawing package",
  "url": "https://canvas.yourschool.edu/courses/YOUR_COURSE_ID/pages/..."
}
```

#### Image References
```json
{
  "content_type": "image_reference", 
  "text": "[Image: 18-1525 - 624 - Bistro - Cafe - Internal Elevations and plan 1 of 2.jpg]",
  "image_url": "https://canvas.yourschool.edu/courses/YOUR_COURSE_ID/files/FILE_ID/preview?...",
  "alt_text": "18-1525 - 624 - Bistro - Cafe - Internal Elevations and plan 1 of 2.jpg",
  "page_title": "construction drawing package"
}
```

### Query Processing

#### Image Query Detection
```python
# Keywords that trigger enhanced image retrieval
image_keywords = ["image", "show", "visual", "picture", "drawing", "diagram", "photo", "figure", "display", "view", "see", "example"]

# Phrases that indicate image requests  
image_phrases = ["show me", "can you show", "any image", "an image", "example of", "visual example"]
```

#### Enhanced Image Retrieval
For image-related queries:
1. Query vector store filtered by `content_type: "image_reference"`
2. Combine with regular hybrid retrieval results
3. Prioritize image references in final results
4. Pass enhanced context to LLM

### LLM Integration

#### System Prompt Strategy
- Explicitly tell LLM it has access to image references
- Instruct to format URLs as clickable markdown links
- Emphasize architectural domain expertise
- Specify capabilities and limitations clearly

#### Context Formation
```python
user_prompt = f"""Question: {prompt}

Available Text Context:
{context_text}

Available Images ({len(image_references)} image references found):
{formatted_image_list}

IMPORTANT INSTRUCTIONS FOR YOUR RESPONSE:
- You have access to {len(image_references)} image references
- ALWAYS provide clickable markdown links: [Image Description](URL)
- These images are real and viewable via the provided URLs
"""
```

## Known Issues & Limitations

### 1. BM25 Initialization Warnings
- **Issue**: Sparse retrieval shows "BM25 index not initialized" 
- **Impact**: Only vector search active (hybrid search disabled)
- **Solution**: Debug BM25 index building in vector store

### 2. Vision Analysis Caching
- **Issue**: Vision AI calls could be optimized for better performance
- **Impact**: Repeated analysis of same images
- **Solution**: Implement more intelligent caching strategies

### 3. Limited Multimodal Understanding
- **Issue**: Using text-only embeddings for storage
- **Impact**: Cannot semantically understand image-text relationships
- **Solution**: Implement true multimodal embeddings (e.g., CLIP, Nomic)

## Development Priorities

### Phase 3: Performance & Retrieval Enhancement  
1. Fix BM25 sparse retrieval initialization
2. Implement proper hybrid fusion
3. Add SPLADE v2 for enhanced sparse retrieval
4. Optimize vision AI caching and performance

### Phase 4: True Multimodal
1. Implement multimodal embeddings
2. Joint text-image semantic search
3. Cross-modal retrieval capabilities
4. Enhanced visual reasoning

### Phase 5: Advanced Features
1. LTI integration for Canvas
2. Auto-sync with Canvas updates
3. Advanced analytics and feedback
4. Mobile-responsive interface
