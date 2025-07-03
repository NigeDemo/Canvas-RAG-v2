# Quick Start Guide for New Contributors

## For New Developers/Agents

### Understanding the Project in 5 Minutes

1. **What it does**: Lets architecture students ask natural language questions about Canvas course content
2. **How it works**: Downloads Canvas pages → Extracts text & image refs → Stores in vector DB → GPT-4 answers questions
3. **Current state**: Phase 1 complete - works well for text, references images by filename only
4. **Next goal**: Add vision AI to actually "see" and describe architectural drawings

### Key Files to Understand

```
src/ui/chat_app.py          # Main Streamlit interface
src/indexing/vector_store.py # ChromaDB operations & retrieval
src/processing/content_processor.py # Canvas content processing
scripts/run_pipeline.py     # End-to-end pipeline
```

### Current Data Flow
```
Canvas HTML → BeautifulSoup → Text chunks + Image URLs → OpenAI embeddings → ChromaDB → Vector search → GPT-4 synthesis
```

### Running the System
```bash
1. Copy .env.example to .env (add your API keys)
2. python scripts/run_pipeline.py --course-id YOUR_COURSE_ID --page-url your-page-slug
3. streamlit run src/ui/chat_app.py
```

### Known Issues Needing Work
1. **BM25 not initializing** - only vector search works
2. **No actual image analysis** - just filename matching
3. **Need vision AI integration** for Phase 2

### Architecture Context
- **Domain**: Architecture education, technical drawings
- **Users**: Students learning construction drawing standards
- **Content**: Canvas LMS pages with embedded architectural drawings
- **Challenge**: Making technical visual content searchable and queryable
