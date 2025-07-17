# Canvas RAG v2 - Multimodal Architecture Drawing Assistant

An intelligent RAG system that enables architecture students to query Canvas LMS content using natural language, with specialized support for architectural drawing content and enhanced LLM-powered responses.

## 🎯 Overview

This system provides a natural-language interface to query Canvas LMS pages containing:
- HTML pages with embedded architectural drawings
- Text content about construction standards and techniques
- Image references with intelligent retrieval and description
- **Vision AI analysis of architectural drawings and technical content**

### Key Features

- **Canvas Integration**: Direct integration with Canvas LMS API for content ingestion
- **Intelligent Retrieval**: Vector-based search with hybrid retrieval capabilities
- **LLM-Powered Responses**: Uses GPT-4 for intelligent reasoning and synthesis
- **Vision AI Analysis**: GPT-4 Vision integration for analyzing architectural drawings
- **Image-Aware Queries**: Specialized handling for image-related questions with content analysis
- **Source Linking**: Provides clickable links back to original Canvas content and images
- **Interactive Chat**: Streamlit-based chat interface with debug capabilities
- **Flexible Ingestion**: Support for both full course and single-page ingestion

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Canvas API    │───▶│   Data Pipeline  │───▶│   Vector Store  │
│                 │    │                  │    │   (ChromaDB)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Chat Interface │◀───│  RAG Pipeline    │◀───│ Hybrid Retrieval│
│  (Streamlit)    │    │   (GPT-4)        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## � Repository Statistics

- **Language**: Python
- **Framework**: Streamlit + OpenAI
- **Database**: ChromaDB  
- **Status**: Phase 2 Complete ✅

## �🚀 Quick Start

### Prerequisites

- Python 3.9+
- Canvas LMS API token
- OpenAI API key

### Installation

```bash
git clone <repository-url>
cd Canvas-RAG-v2
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.template` to `.env`
2. Add your Canvas API token and OpenAI API key
3. Configure Canvas base URL

### Usage

#### Option 1: Full Course Ingestion
```bash
# 1. Ingest entire Canvas course
python scripts/run_pipeline.py --course-id YOUR_COURSE_ID

# 2. Start vision-enhanced chat interface
streamlit run src/ui/vision_chat_app.py
```

#### Option 2: Single Page Ingestion
```bash
# 1. Ingest a specific Canvas page by URL slug
python scripts/run_pipeline.py --course-id YOUR_COURSE_ID --page-url your-page-slug

# 2. Start vision-enhanced chat interface  
streamlit run src/ui/vision_chat_app.py
```

#### Option 3: Programmatic Single Page Ingestion
```python
# Ingest a specific Canvas page by URL slug
from src.ingestion.canvas_ingester import CanvasIngester
import asyncio

async def ingest_single_page():
    async with CanvasIngester() as ingester:
        # Replace with your actual course ID and page URL slug
        metadata = await ingester.ingest_specific_page(
            course_id="12345",
            page_url="construction-drawing-package-2"
        )
        print(f"Ingested page: {metadata['page']['title']}")

asyncio.run(ingest_single_page())
```

#### Interactive Demo
```bash
# Run the comprehensive Jupyter notebook demo
jupyter notebook notebooks/Canvas_RAG_Demo.ipynb
```

## 📁 Project Structure

```
Canvas-RAG-v2/
├── src/
│   ├── ingestion/          # Canvas API and content extraction
│   ├── processing/         # PDF to image, chunking
│   ├── embeddings/         # Multimodal embedding models
│   ├── indexing/          # Vector store and sparse indexing
│   ├── retrieval/         # Hybrid search implementation
│   ├── generation/        # LLM integration and prompting
│   ├── vision/            # Vision AI integration
│   ├── ui/               # Streamlit chat interface
│   └── utils/            # Common utilities
├── setup/               # Setup and configuration scripts
├── scripts/             # Utility scripts
├── tests/               # Unit and integration tests
├── data/                # Raw and processed data
├── docs/               # Documentation
└── logs/               # Application logs
```

## 🛣️ Development Phases

### Phase 1: Current Implementation ✅
- ✅ Canvas API integration
- ✅ Text content processing and chunking
- ✅ OpenAI embeddings (text-embedding-3-large)
- ✅ ChromaDB vector storage
- ✅ Image reference extraction and indexing
- ✅ GPT-4 powered response generation
- ✅ Streamlit chat interface with debug features
- ✅ Enhanced image query detection
- ✅ Clickable source links and image URLs

### Phase 2: Visual Analysis Enhancement ✅
- ✅ Vision AI integration (GPT-4 Vision/Claude Vision)
- ✅ Automatic image content analysis
- ✅ OCR extraction from architectural drawings
- ✅ Enhanced visual reasoning capabilities

### Phase 3: Retrieval Improvements
- [ ] BM25 sparse retrieval implementation
- [ ] SPLADE v2 integration
- [ ] Advanced hybrid fusion
- [ ] Performance optimization

### Phase 4: UI/UX Enhancements
- [ ] Enhanced chat interface
- [ ] User feedback collection
- [ ] Chat history and analytics
- [ ] Mobile-responsive design

### Phase 5: Canvas Integration
- [ ] LTI (Learning Tools Interoperability) plugin
- [ ] Auto-sync with Canvas updates
- [ ] Embedded chat widget

## ⚠️ Current Limitations & Future Enhancements

### Current State (Phase 2 Complete)
**What Works:**
- ✅ Canvas content ingestion and processing
- ✅ Text-based search and retrieval
- ✅ Image reference extraction and linking
- ✅ GPT-4 powered intelligent responses
- ✅ Interactive chat interface
- ✅ **Vision AI Analysis**: GPT-4 Vision integration for architectural drawing analysis
- ✅ **OCR Capabilities**: Text extraction from architectural drawings
- ✅ **Enhanced Visual Reasoning**: Detailed analysis of electrical plans, elevations, and technical drawings

**Current Limitations:**
- ⚠️ **BM25 Not Active**: Sparse retrieval shows warnings (vector search only)
- ⚠️ **Vision Analysis Caching**: Could be optimized for better performance

### Next Priority Enhancements (Phase 3)
1. **BM25 Integration**: Implement and fix sparse retrieval for enhanced search
2. **Vision Analysis Caching**: Optimize vision AI calls with intelligent caching
3. **Advanced Hybrid Fusion**: Improve retrieval ranking and fusion algorithms
4. **Performance Optimization**: Enhance response times and resource usage

## 📋 **For New Contributors/Agents**

**Quick Understanding**: This system helps architecture students query Canvas course content in natural language. Phase 1 (text search + image filename matching) and Phase 2 (vision AI integration) are complete. Phase 3 priority is optimizing retrieval and performance.

**Key Files**: `src/ui/chat_app.py` (interface), `src/ui/vision_chat_app.py` (vision-enhanced interface), `src/indexing/vector_store.py` (retrieval), `src/vision/vision_rag_integration.py` (vision AI), `scripts/run_pipeline.py` (ingestion)

**Test It**: Set up `.env` file → Run pipeline → Start Streamlit app → Ask "Can you describe the electrical plan?" for vision AI demo 

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/retrieval/
```

## 📊 Evaluation

The system includes comprehensive evaluation metrics:
- Retrieval accuracy (Recall@K, Precision@K)
- Answer quality assessment
- Source citation accuracy
- User feedback analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

#### When to Use Single Page vs Full Course Ingestion

**Use Single Page Ingestion When:**
- Testing the system with a specific page
- Working with frequently updated content that needs re-ingestion  
- Processing only specific modules or assignments
- Limiting scope for performance or cost reasons
- Debugging content extraction issues

**Use Full Course Ingestion When:**
- Setting up the system for the first time
- Need comprehensive coverage of all course materials
- Students will query across multiple topics/modules
- Building a complete knowledge base

#### Example Page URL Slugs
Canvas page URLs typically have slugs like:
- `construction-drawing-package-2`
- `architectural-standards-week-3`
- `dimensioning-conventions-tutorial`
- `building-sections-and-details`

You can find the page slug in the Canvas URL:
`https://yourschool.instructure.com/courses/YOUR_COURSE_ID/pages/your-page-slug`
                                                           ↑ This is the page slug
