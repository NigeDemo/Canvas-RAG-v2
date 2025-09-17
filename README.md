# Canvas RAG v2 - Multimodal Architecture Drawing Assistant

An intelligent RAG system that enables architecture students to query Canvas LMS content using natural language, with specialized support for architectural drawing content, section-aware text processing, and enhanced LLM-powered responses.

## 🎯 Overview

This system provides a natural-language interface to query Canvas LMS pages containing:
- HTML pages with embedded architectural drawings
- Text content about construction standards and techniques with **section-aware processing**
- Image references with intelligent retrieval and description
- **Vision AI analysis of architectural drawings and technical content**
- **Structured page content with section heading detection**

### Key Features

- **Canvas Integration**: Direct integration with Canvas LMS API for content ingestion
- **Section-Aware Processing**: Automatic detection and separate indexing of page sections and headings
- **Intelligent Query Enhancement**: Automatic expansion of user queries with architectural synonyms and context terms
- **Hybrid Retrieval**: Vector-based search (50% semantic) combined with BM25 sparse search (50% keyword)
- **LLM-Powered Responses**: Uses GPT-4 for intelligent reasoning and synthesis
- **Vision AI Analysis**: GPT-4 Vision integration for analyzing architectural drawings
- **Structure Queries**: Support for "what sections are on this page?" type queries
- **Image-Aware Queries**: Specialized handling for image-related questions with content analysis
- **Source Linking**: Provides clickable links back to original Canvas content and images
- **Interactive Chat**: Streamlit-based chat interface with debug capabilities
- **Flexible Ingestion**: Support for both full course and single-page ingestion

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Canvas API    │───▶│ Section-Aware    │───▶│   Vector Store  │
│                 │    │  Data Pipeline   │    │   (ChromaDB)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Chat Interface │◀───│  RAG Pipeline    │◀───│ Hybrid Retrieval│
│  (Streamlit)    │    │   (GPT-4)        │    │ + Section Query │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ Vision AI       │
                                              │ (GPT-4 Vision)  │
                                              └─────────────────┘
```

## 📊 Repository Statistics

- **Language**: Python
- **Framework**: Streamlit + OpenAI
- **Database**: ChromaDB  
- **Status**: Phase 2+ Complete (Section-Aware) ✅

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

#### Query Enhancement Settings (Optional)
```bash
# Query enhancement is enabled by default
ENABLE_QUERY_ENHANCEMENT=true

# Limit number of enhancement terms (default: 10)
QUERY_ENHANCEMENT_MAX_TERMS=10

# Enable debug logging to see enhanced queries
QUERY_ENHANCEMENT_DEBUG=true

# Adjust hybrid search weighting (default: 0.5 = 50/50 semantic/keyword)
HYBRID_FUSION_ALPHA=0.5
```

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
├── tests/               # Limited unit tests and validation scripts
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

### Phase 2+: Section-Aware Architecture ✅
- ✅ Automatic section detection from Canvas pages
- ✅ Section-aware text chunking and indexing
- ✅ Structure query support ("what sections are on this page?")
- ✅ Section heading prioritization in retrieval
- ✅ Enhanced page organization understanding

### Phase 2++: Query Enhancement ✅
- ✅ Intelligent query expansion with architectural synonyms
- ✅ Question type-specific enhancement (what/how/where/when/why)
- ✅ Section query enhancement (headings, structure, topics)
- ✅ Visual reasoning enhancement (diagram, display, graphic)
- ✅ Configurable enhancement settings and debug logging
- ✅ Hybrid search weighting control (semantic vs keyword balance)

### Phase 3: Retrieval Improvements
- ✅ BM25 sparse retrieval implementation (available)
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

### Current State (Phase 2+ Complete)
**What Works:**
- ✅ Canvas content ingestion and processing
- ✅ Section-aware text processing and chunking
- ✅ Text-based search and retrieval with section prioritization
- ✅ Image reference extraction and linking
- ✅ GPT-4 powered intelligent responses
- ✅ Interactive chat interface
- ✅ **Vision AI Analysis**: GPT-4 Vision integration for architectural drawing analysis
- ✅ **OCR Capabilities**: Text extraction from architectural drawings
- ✅ **Enhanced Visual Reasoning**: Detailed analysis of electrical plans, elevations, and technical drawings
- ✅ **Section Structure Queries**: Support for "what sections are on this page?" queries

**Current Limitations:**
- ✅ **BM25 Active**: Sparse retrieval implemented and functional
- ⚠️ **Vision Analysis Caching**: Could be optimized for better performance

### Next Priority Enhancements (Phase 3)
1. **Advanced Hybrid Fusion**: Improve retrieval ranking and fusion algorithms
2. **Vision Analysis Caching**: Optimize vision AI calls with intelligent caching
3. **Performance Optimization**: Enhance response times and resource usage
4. **Embedding Model Optimization**: Address quota management and alternative models

## 📋 **For New Contributors/Agents**

**Quick Understanding**: This system helps architecture students query Canvas course content in natural language. Phase 1 (text search + image filename matching) and Phase 2 (vision AI integration) are complete. Phase 3 priority is optimizing retrieval and performance.

**Key Files**: `src/ui/chat_app.py` (interface), `src/ui/vision_chat_app.py` (vision-enhanced interface), `src/indexing/vector_store.py` (retrieval), `src/vision/vision_rag_integration.py` (vision AI), `scripts/run_pipeline.py` (ingestion)

**Test It**: Set up `.env` file → Run `python scripts/validate_setup.py` → Run pipeline → Start Streamlit app → Ask "Can you describe the electrical plan?" for vision AI demo 

---

## 🧪 Testing & Validation

### System Validation
```bash
# Validate system configuration and setup
python scripts/validate_setup.py
```

### Unit Tests (Limited Coverage)
```bash
# Run the available unit tests
pytest tests/

# Specific test files:
pytest tests/test_processing.py      # Content processing unit tests
pytest tests/test_vision_config.py  # Vision AI configuration check
pytest tests/test_vision_ai.py      # Vision AI integration test
pytest tests/test_image_processing.py # Image processing validation
```

### Manual Testing
```bash
# Test the complete system end-to-end
# 1. Set up environment
cp .env.template .env
# Add your API keys to .env

# 2. Validate setup
python scripts/validate_setup.py

# 3. Ingest content
python scripts/run_pipeline.py --course-id YOUR_COURSE_ID

# 4. Test vision AI
streamlit run src/ui/vision_chat_app.py
# Ask: "Can you describe the electrical plan?"
```

**Testing Notes**: 
- Limited unit test coverage - mostly configuration validation
- No comprehensive test suite for regression testing
- Manual end-to-end testing recommended for validation
- Future development should prioritize adding proper unit tests

## 📊 Evaluation

The system includes comprehensive evaluation metrics:
- Retrieval accuracy (Recall@K, Precision@K)
- Answer quality assessment
- Source citation accuracy
- User feedback analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add functionality with proper error handling
4. **Add unit tests** (current coverage is limited - help needed!)
5. Update documentation as needed
6. Submit a pull request

**Note**: The project currently has limited unit test coverage. Contributing proper unit tests with mocking and isolation would be highly valuable!

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
