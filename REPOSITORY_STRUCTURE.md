# Canvas RAG v2 - Repository Organization

## 📁 Directory Structure & Naming Conventions

### Top-Level Organization

```
Canvas-RAG-v2/
├── scripts/              ← Pipeline orchestrators (user-facing entry points)
├── src/                  ← Core modules (reusable components)
├── data/                 ← Data storage (raw, processed, vector DB)
├── docs/                 ← Documentation
├── tests/                ← Unit and integration tests
├── logs/                 ← Application logs
└── setup/                ← Setup and configuration scripts
```

---

## 🔧 Scripts Directory - Pipeline Orchestrators

**Purpose:** User-facing entry points that orchestrate the complete pipeline

### Main Pipeline Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_pipeline.py` | Single page or full course | Standard pipeline for 1 page or all pages |
| `run_multi_page_pipeline.py` | Multiple specific pages | Batch processing for selected pages |

**Command Examples:**
```powershell
# Single page
python scripts/run_pipeline.py --page-url "construction-drawing-package-2"

# Full course
python scripts/run_pipeline.py --course-id 45166

# Multiple specific pages (edit script first)
python scripts/run_multi_page_pipeline.py
```

### Utility Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `rebuild_index.py` | Rebuild indices from existing processed data | After changing embedding model or index settings |
| `demo_single_page.py` | Demo/testing for single page | Testing new features |
| `quick_start.py` | Initial project setup | First time setup |

---

## 📦 Source Directory - Core Modules

**Purpose:** Reusable components used by pipeline scripts

### Module Organization

```
src/
├── config/                    ← Configuration management
│   ├── settings.py           ← Centralized settings (loads .env)
│   └── __init__.py
│
├── ingestion/                 ← Canvas LMS interaction
│   ├── canvas_ingester.py    ← Canvas API client (uses canvasapi library)
│   └── __init__.py
│
├── processing/                ← Content processing
│   ├── content_processor.py  ← Section-aware chunking, text extraction
│   └── __init__.py
│
├── indexing/                  ← Vector & sparse indexing
│   ├── vector_store.py       ← VectorStore, SparseIndex, HybridRetriever, IndexBuilder
│   └── __init__.py
│
├── retrieval/                 ← Search & retrieval
│   ├── hybrid_search.py      ← HybridSearchEngine, QueryProcessor
│   └── __init__.py
│
├── embeddings/                ← Embedding generation
│   ├── embedding_manager.py  ← EmbeddingManager (OpenAI, sentence-transformers)
│   └── __init__.py
│
├── generation/                ← Response generation
│   ├── llm_integration.py    ← LLM response generation
│   ├── vision_enhanced_generator.py  ← Vision-enhanced responses
│   └── __init__.py
│
├── vision/                    ← Vision AI processing
│   ├── vision_processor.py   ← VisionProcessor (GPT-4V, Claude)
│   ├── vision_rag_integration.py  ← VisionEnhancedRAG
│   ├── image_analyzer.py     ← ImageAnalyzer
│   └── __init__.py
│
├── ui/                        ← User interfaces
│   ├── chat_app.py           ← Basic Streamlit chat
│   ├── vision_chat_app.py    ← Vision-enhanced Streamlit chat
│   └── __init__.py
│
└── utils/                     ← Utilities
    ├── logger.py             ← Centralized logging
    └── __init__.py
```

### Key Classes by Module

#### `ingestion/canvas_ingester.py`
- `CanvasIngester` - Canvas API interaction
  - `ingest_course_content(course_id)` - Get all pages from course
  - `ingest_specific_page(course_id, page_url)` - Get single page

#### `processing/content_processor.py`
- `ContentProcessor` - Content processing with vision AI
  - `process_course_content(metadata_path)` - Process ingested content
  - Section-aware chunking with heading detection

#### `indexing/vector_store.py`
- `VectorStore` - ChromaDB interface
- `SparseIndex` - BM25 sparse index
- `HybridRetriever` - Vector + BM25 retrieval with RRF fusion
- `IndexBuilder` - High-level index management

#### `retrieval/hybrid_search.py`
- `HybridSearchEngine` - Main search orchestrator
- `QueryProcessor` - Query analysis and enhancement

#### `generation/llm_integration.py`
- `RAGPipeline` - Response generation with LLM

#### `vision/vision_rag_integration.py`
- `VisionEnhancedRAG` - Vision-enhanced RAG system

---

## 💾 Data Directory - Storage

```
data/
├── raw/                       ← Raw ingested data from Canvas
│   ├── course_*_metadata.json     ← Full course metadata
│   ├── page_*_metadata.json       ← Single page metadata
│   └── files/                     ← Downloaded PDFs and images
│
├── processed/                 ← Processed content ready for indexing
│   ├── processed_*.json           ← Processed segments
│   └── processed_multi_page_consolidated.json  ← Batch consolidated
│
├── chroma_db/                 ← ChromaDB vector database
│   ├── chroma.sqlite3
│   └── [collection data]
│
└── cache/                     ← Vision AI cache (pickled responses)
    └── openai_*.pkl
```

---

## 📚 Documentation Directory

```
docs/
├── API.md                     ← API reference (if needed)
├── MULTI_PAGE_INGESTION.md   ← Guide for multi-page processing
└── [other guides]
```

---

## 🧪 Tests Directory

```
tests/
├── conftest.py                ← Pytest configuration
├── test_*.py                  ← Unit tests
└── integration/               ← Integration tests
```

---

## 🔄 Data Flow

### Complete Pipeline Flow

```
1. INGESTION (Canvas API → Raw Data)
   scripts/run_pipeline.py 
   or 
   scripts/run_multi_page_pipeline.py
        ↓
   Uses: src/ingestion/canvas_ingester.py
        ↓
   Output: data/raw/page_*_metadata.json + files/

2. PROCESSING (Raw Data → Processed Segments)
   Uses: src/processing/content_processor.py
        ↓
   - Section-aware chunking
   - Text extraction
   - Image reference handling
   - Optional: Vision AI analysis
        ↓
   Output: data/processed/processed_*.json

3. INDEXING (Processed Segments → Searchable Indices)
   Uses: src/indexing/vector_store.py
        ↓
   - Generate embeddings (src/embeddings/embedding_manager.py)
   - Store in ChromaDB (Vector)
   - Build BM25 index (Sparse)
        ↓
   Output: data/chroma_db/ (persistent)

4. RETRIEVAL (User Query → Relevant Content)
   Uses: src/retrieval/hybrid_search.py
        ↓
   - Query enhancement
   - Hybrid search (Vector + BM25 with RRF)
   - Result ranking
        ↓
   Returns: Top N relevant segments

5. GENERATION (Content → User Response)
   Uses: src/generation/llm_integration.py
        OR
        src/vision/vision_rag_integration.py (for vision queries)
        ↓
   - LLM prompt construction
   - Optional: Vision analysis
   - Response generation
        ↓
   Returns: Natural language answer
```

---

## 🏷️ Naming Conventions

### Files
- **Pipeline scripts:** `run_*.py` - Orchestrators
- **Core modules:** `*_manager.py`, `*_processor.py`, `*_ingester.py` - Component classes
- **Tests:** `test_*.py` - Unit/integration tests
- **Utilities:** Descriptive names (e.g., `logger.py`)

### Classes
- **Managers:** `*Manager` (e.g., `EmbeddingManager`)
- **Processors:** `*Processor` (e.g., `ContentProcessor`, `QueryProcessor`)
- **Builders:** `*Builder` (e.g., `IndexBuilder`)
- **Engines:** `*Engine` (e.g., `HybridSearchEngine`)

### Functions
- **Public API:** Snake_case (e.g., `process_course_content`)
- **Internal/Private:** Leading underscore (e.g., `_extract_sections`)

### Constants
- **Environment variables:** UPPER_SNAKE_CASE (e.g., `CANVAS_API_KEY`)
- **Module constants:** UPPER_SNAKE_CASE (e.g., `MAX_CHUNK_SIZE`)

---

## 🎯 Key Principles

### 1. Separation of Concerns
- **Scripts** = Entry points & orchestration
- **Modules** = Reusable components & business logic

### 2. Modularity
- Each module has a single responsibility
- Modules can be imported and used independently
- Easy to test and maintain

### 3. Data Flow
- Clear unidirectional flow: Ingest → Process → Index → Retrieve → Generate
- Each stage produces persistent artifacts
- Stages can be re-run independently (e.g., rebuild index without re-ingesting)

### 4. Configuration
- Centralized in `src/config/settings.py`
- Environment variables in `.env`
- No hardcoded configuration in modules

---

## 📖 Quick Reference

### I want to...

**Process a single Canvas page:**
```powershell
python scripts/run_pipeline.py --page-url "my-page"
```

**Process multiple specific pages:**
```powershell
# Edit scripts/run_multi_page_pipeline.py first
python scripts/run_multi_page_pipeline.py
```

**Process entire course:**
```powershell
python scripts/run_pipeline.py --course-id 45166
```

**Rebuild indices with new settings:**
```powershell
python scripts/rebuild_index.py
```

**Test a query:**
```powershell
python scripts/demo_single_page.py
```

**Start chat interface:**
```powershell
streamlit run src/ui/vision_chat_app.py
```

---

## 🔍 Finding Things

### "Where is the Canvas API code?"
→ `src/ingestion/canvas_ingester.py`

### "Where is the section-aware chunking?"
→ `src/processing/content_processor.py`

### "Where is the BM25 implementation?"
→ `src/indexing/vector_store.py` (class `SparseIndex`)

### "Where is the hybrid search logic?"
→ `src/retrieval/hybrid_search.py`

### "Where is query enhancement?"
→ `src/retrieval/hybrid_search.py` (class `QueryProcessor`)

### "Where is the vision AI integration?"
→ `src/vision/vision_rag_integration.py`

### "Where is the chat interface?"
→ `src/ui/vision_chat_app.py`

---

**Last Updated:** October 2, 2025  
**Repository:** Canvas-RAG-v2  
**Maintainer:** Architecture Education System
