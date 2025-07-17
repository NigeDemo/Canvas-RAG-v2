# Quick Start Guide for New Contributors

## For New Developers/Agents

### Understanding the Project in 5 Minutes

1. **What it does**: Lets architecture students ask natural language questions about Canvas course content
2. **How it works**: Downloads Canvas pages → Extracts text & image refs → Stores in vector DB → GPT-4 + Vision AI answers questions
3. **Current state**: Phase 2 complete - works well for text AND can analyze architectural drawings visually
4. **Next goal**: Performance optimization and BM25 integration (Phase 3)

### Key Files to Understand

```
src/ui/vision_chat_app.py    # Vision-enhanced Streamlit interface
src/vision/vision_rag_integration.py # Vision AI integration
src/indexing/vector_store.py # ChromaDB operations & retrieval
src/processing/content_processor.py # Canvas content processing
scripts/run_pipeline.py     # End-to-end pipeline
```

### Current Data Flow
```
Canvas HTML → BeautifulSoup → Text chunks + Image URLs → OpenAI embeddings → ChromaDB → Vector search → Vision AI analysis → GPT-4 synthesis
```

### Running the System
```bash
1. Copy .env.template to .env (add your API keys)
2. python scripts/run_pipeline.py --course-id YOUR_COURSE_ID --page-url your-page-slug
3. streamlit run src/ui/vision_chat_app.py
```

### Current Capabilities ✅
1. **Text-based queries** - Full semantic search
2. **Image analysis** - GPT-4 Vision integration for architectural drawings
3. **OCR extraction** - Text extraction from technical drawings
4. **Visual reasoning** - Detailed analysis of electrical plans, elevations, etc.

### Known Issues Needing Work
1. **BM25 not initializing** - only vector search works
2. **Vision caching** - Could be optimized for better performance
3. **Multimodal embeddings** - Currently using text-only embeddings

### Architecture Context
- **Domain**: Architecture education, technical drawings
- **Users**: Students learning construction drawing standards
- **Content**: Canvas LMS pages with embedded architectural drawings
- **Challenge**: Making technical visual content searchable and queryable

### Test the Vision AI
Ask questions like:
- "Can you describe the electrical plan?"
- "What rooms are shown in this floor plan?"
- "What are the dimensions shown in this drawing?"
