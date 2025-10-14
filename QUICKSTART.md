# Quick Start Guide for New Contributors

## For New Developers/Agents

### Understanding the Project in 5 Minutes

1. **What it does**: Lets architecture students ask natural language questions about Canvas course content with support for page structure queries and intelligent query enhancement
2. **How it works**: Downloads Canvas pages → Section-aware text processing → Query enhancement → Extracts text & image refs → Stores in vector DB → GPT-4 + Vision AI answers questions
3. **Current state**: Phase 2++ complete - works well for text AND can analyze architectural drawings visually AND understands page structure AND enhances queries intelligently
4. **Next goal**: Performance optimization and embedding model resolution (Phase 3)

### Key Files to Understand

```
src/ui/vision_chat_app.py    # Vision-enhanced Streamlit interface
src/vision/vision_rag_integration.py # Vision AI integration
src/retrieval/hybrid_search.py # Query enhancement and hybrid search engine
src/indexing/vector_store.py # ChromaDB operations & section-aware retrieval
src/processing/content_processor.py # Section-aware Canvas content processing
scripts/run_pipeline.py     # End-to-end pipeline with section detection
```

### Current Data Flow
```
Canvas HTML → Section Detection → Section-aware chunking → Query Enhancement → Text chunks + Image URLs → OpenAI embeddings → ChromaDB → Vector search + Section prioritization → Vision AI analysis → GPT-4 synthesis
```

### Recent Major Update (January 2025)
- ✅ **Query Enhancement**: Intelligent expansion with architectural synonyms and optimization
- ✅ **Section-Aware Architecture**: System now detects and separately indexes page section headings
- ✅ **Structure Queries**: Supports "what sections are on this page?" queries
- ✅ **Enhanced Retrieval**: Section headings prioritized for structure-related queries
- ✅ **Section Query Bug Fix**: Fixed section heading retrieval prioritization (Aug 1, 2025)
- ✅ **OpenAI Integration**: Fully functional with rate limiting protection
- ✅ **Production Testing**: Query enhancement validated in Streamlit chat interface

### Running the System

**First-time setup:**
```bash
# 1. Activate virtual environment (if you have one)
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -e .

# 3. Copy .env.template to .env and add your API keys
copy .env.template .env  # Windows
# cp .env.template .env  # macOS/Linux

# 4. Configure query enhancement (optional)
# ENABLE_QUERY_ENHANCEMENT=true        # Enable intelligent query expansion
# QUERY_ENHANCEMENT_MAX_TERMS=10       # Maximum additional terms to add
# QUERY_ENHANCEMENT_DEBUG=true         # Enable debug logging

# 5. Validate your setup
python scripts\validate_setup.py
```

**Run the pipeline (with section-aware processing):**
```bash
# For single page with section detection (recommended)
python scripts\run_pipeline.py --course-id YOUR_COURSE_ID --page-url construction-drawing-package-2

# For full course ingestion (when OpenAI quota available)
python scripts\run_pipeline.py --course-id YOUR_COURSE_ID --embedding-model openai

# For single page ingestion (with OpenAI embeddings)
python scripts\run_pipeline.py --course-id YOUR_COURSE_ID --page-url your-page-slug --embedding-model openai
```

**⚠️ If you have database issues:**
```bash
# Clear the database and restart with OpenAI embeddings
rm -rf data/chroma_db/*  # macOS/Linux
# rmdir /s data\chroma_db  # Windows (use with caution)

# Then re-run pipeline
python scripts\run_pipeline.py --course-id YOUR_COURSE_ID --page-url your-page-slug --embedding-model openai
```

**Start the chat interface:**
```bash
# Vision-enhanced interface (recommended)
streamlit run src\ui\vision_chat_app.py
# OR use: .venv\Scripts\python.exe -m streamlit run src\ui\vision_chat_app.py

# Basic interface (fallback)
streamlit run src\ui\chat_app.py
```

**⚠️ Important Note:**
Before asking questions, you need to run the pipeline to ingest Canvas content:
```bash
python scripts\run_pipeline.py --course-id YOUR_COURSE_ID --page-url your-page-slug
```

**Optional: Quick smoke test for image retrieval**
```bash
# Validate that image queries return Canvas image links and a concise response
python scripts\smoke_test_images.py
```
Expected: Each query prints SUCCESS: True, a list of image URLs, and the start of an answer.

**VS Code Users:**
You can also use the pre-configured tasks:
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Vision Chat App"
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Install Dependencies"
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Setup Vision AI"

### Current Capabilities ✅
1. **Text-based queries** - Full semantic search with intelligent query enhancement
2. **Image analysis** - GPT-4 Vision integration for architectural drawings
3. **OCR extraction** - Text extraction from technical drawings
4. **Visual reasoning** - Detailed analysis of electrical plans, elevations, etc.
5. **Query Enhancement** - Automatic expansion with architectural synonyms
6. **Structure Queries** - Support for "what sections are on this page?" queries

### Known Issues Needing Work
1. **BM25** - Active in current build (auto-populates from existing text docs). If you see sparse index count = 0, rebuild index or check logs.
2. **Vision caching** - Could be optimized for better performance
3. **Multimodal embeddings** - Currently using text-only embeddings

### Architecture Context
- **Domain**: Architecture education, technical drawings
- **Users**: Students learning construction drawing standards
- **Content**: Canvas LMS pages with embedded architectural drawings
- **Challenge**: Making technical visual content searchable and queryable

### Test the Vision AI & Query Enhancement
Ask questions like:
- "Can you describe the electrical plan?" (automatically enhanced with electrical terms)
- "What rooms are shown in this floor plan?" (floor plan enhanced to layout, site plan)
- "What are the dimensions shown in this drawing?" (enhanced for visual reasoning)
- "What sections are on this page?" (enhanced for structure queries)
- "How to create elevations?" (how enhanced to method, technique, procedure)
