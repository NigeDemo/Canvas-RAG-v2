# Technical Implementation Notes

## Quick Context for New Contributors

**Project**: Canvas RAG v2 - Architecture course content assistant  
**Domain**: Architecture education, technical drawing analysis  
**Current Status**: Phase 2++ complete (vision AI + section-aware architecture + query enhancement implemented)  
**Next Priority**: Performance optimization and embedding model resolution (Phase 3)  
**Tech Stack**: Canvas API → Python → Section Detection → OpenAI (embeddings + GPT-4 + Vision) → ChromaDB → Streamlit  

---

## Current Architecture (Phase 2+ Complete)

### Data Flow
1. **Canvas Ingestion**: Extract HTML pages and image references
2. **Section-Aware Processing**: Detect page sections and headings automatically
3. **Content Processing**: Parse HTML, extract text with section structure preserved
4. **Section-Based Chunking**: Create separate chunks for headings and content
5. **Vectorization**: Create embeddings using OpenAI text-embedding-3-large
6. **Storage**: Store in ChromaDB with section metadata
7. **Query Enhancement**: Intelligent expansion with architectural synonyms
8. **Enhanced Retrieval**: Vector similarity search with section prioritization
9. **Vision AI Integration**: GPT-4 Vision analysis for architectural drawings
10. **Generation**: GPT-4 synthesis with intelligent prompting and vision analysis

### What Gets Indexed

#### Section Heading Chunks (NEW)
```json
{
  "content_type": "section_heading",
  "text": "Why do we produce a 'Technical', 'Working', or' Construction' Drawing Pack?",
  "section_index": 0,
  "is_section_heading": true,
  "source_id": 1440959,
  "title": "construction drawing package"
}
```

#### Section Content Chunks (NEW)
```json
{
  "content_type": "section_content",
  "text": "Architects and Architectural Technologists produce these drawings...",
  "section_index": 0,
  "chunk_index": 0,
  "source_id": 1440959,
  "title": "construction drawing package"
}
```

#### Text Chunks (Legacy Support)
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

#### Query Enhancement (NEW)
- **Architectural Synonyms**: Automatic expansion of domain-specific terms
  - "floor plan" → "layout", "site plan", "building plan"
  - "elevation" → "facade", "external view", "building front"
  - "section" → "cross-section", "sectional view", "cut"
- **Question Type Optimization**: Enhancement of interrogative queries
  - "how" → "method", "technique", "procedure", "process"
  - "what" → "definition", "explanation", "description"
  - "where" → "location", "position", "placement"
- **Section Query Enhancement**: Intelligent section/structure query processing
  - "sections" → "headings", "structure", "topics", "organization"
- **Visual Reasoning Enhancement**: Improved queries for image analysis
  - "analyze" → "diagram", "display", "graphic", "visual", "illustration"
- **Configuration**: Controlled by ENABLE_QUERY_ENHANCEMENT, max terms limit, debug logging

#### Section Structure Queries (NEW)
- **Detection**: `is_section_heading_query()` identifies structure-related queries
- **Query Patterns**: "what sections", "what headings", "page structure", "section titles"
- **Retrieval**: Section heading chunks prioritized in results
- **Response**: Lists detected section headings and page organization

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

## Implementation Details

### Query Enhancement Configuration
```python
# Environment variables in .env
ENABLE_QUERY_ENHANCEMENT=true
QUERY_ENHANCEMENT_MAX_TERMS=10
QUERY_ENHANCEMENT_DEBUG=true

# Usage in hybrid_search.py
enhanced_query = self.query_processor.enhance_query(
    query=query,
    max_additional_terms=max_terms,
    debug=debug_enabled
)
```

### Debug Logging
Query enhancement operations are logged to `logs/canvas_rag.log`:
```
DEBUG - Query enhancement: 'floor plan' → ['floor plan', 'layout', 'site plan', 'building plan']
DEBUG - Visual reasoning: 'analyze' → ['analyze', 'diagram', 'display', 'graphic']
```

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
