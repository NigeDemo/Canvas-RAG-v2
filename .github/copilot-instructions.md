<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Canvas RAG v2 - Vision AI Integration + Section-Aware Architecture

## Project Context
This is a Canvas RAG v2 system for architecture education that combines text and image content from Canvas LMS. The system is currently in Phase 2+ completion, with vision AI capabilities and section-aware text processing fully implemented and production-ready.

## Key Technical Details

### Architecture Stack
- **Backend**: Python with FastAPI/Streamlit
- **LLM Integration**: OpenAI GPT-4 (text + vision), Anthropic Claude (vision)
- **Vector Database**: ChromaDB for embeddings
- **Canvas Integration**: Canvas LMS API
- **Image Processing**: PIL, pdf2image, vision AI APIs
- **Text Processing**: Section-aware chunking with embedded heading detection

### Current Implementation Status
- **Phase 1 Complete**: Text indexing, basic image filename matching
- **Phase 2 Complete**: Vision AI integration for content analysis
- **Phase 2+ Complete**: Section-aware architecture with heading detection and retrieval bug fixes
- **Repository Clean**: Production-ready codebase with cleaned temporary scripts (Aug 1, 2025)
- **Phase 3 Ready**: Performance optimization and embedding model resolution

### Code Style Guidelines
- Follow existing patterns in the codebase
- Use type hints consistently
- Include comprehensive docstrings
- Maintain the existing logging structure using `get_logger(__name__)`
- Error handling should be robust with proper logging

### Vision AI Integration Features
- ✅ Support for both GPT-4 Vision and Claude Vision APIs
- ✅ Implemented image content analysis for architectural drawings
- ✅ Provide OCR capabilities for text extraction
- ✅ Maintain backward compatibility with existing text-based queries
- ✅ Cache vision analysis results to avoid redundant API calls

### Section-Aware Processing Features (Phase 2+ Complete)
- ✅ Automatic detection of Canvas page section headings
- ✅ Embedded heading recognition within flowing text paragraphs
- ✅ Separate indexing of section headings and section content
- ✅ Structure query support ("what sections are on this page?")
- ✅ Section heading prioritization in retrieval results (bug fixed Aug 1, 2025)
- ✅ Enhanced page organization understanding

### Domain-Specific Context
- **Architecture Education**: Focus on construction drawings, plans, elevations, sections
- **Drawing Types**: Floor plans, site plans, elevations, details, perspectives
- **Technical Elements**: Dimensions, annotations, symbols, hatching patterns
- **Query Types**: Visual reasoning, measurement extraction, content identification

### File Structure
- `src/vision/` - Vision AI integration modules (✅ Complete)
- `src/generation/` - LLM integration and response generation
- `src/processing/` - Content processing including section-aware text processing (✅ Enhanced)
- `src/retrieval/` - Hybrid search and retrieval logic
- `src/indexing/` - Vector database operations with section query support (✅ Enhanced)

### Key Implementation Files
- `src/processing/content_processor.py` - Section detection and chunking logic
- `src/indexing/vector_store.py` - Enhanced retrieval with section prioritization (bug fixed)
- `scripts/run_pipeline.py` - Main pipeline with section-aware processing
- `debug_db.py` - Database inspection tool (essential debugging)
- `check_section_headings.py` - Section detection verification tool

### Testing Strategy
- Unit tests for vision processing functions
- Integration tests for section detection and chunking
- Structure query testing for page organization features
- Debug tools available for troubleshooting (cleaned repository Aug 1, 2025)

### Current Status & Known Issues
- ✅ OpenAI embedding integration working with rate limiting protection
- ✅ Section heading retrieval bug fixed (Aug 1, 2025)
- ✅ BM25 sparse index fully functional for hybrid retrieval
- ✅ Repository cleaned of temporary scripts and debug files
- ⚠️ Section detection: Currently finds 4/5 target headings (needs investigation)
- ⚠️ Chat UI testing: Section queries tested in CLI but not fully verified in Streamlit interface

### Next Session Priorities
- Complete fresh pipeline run with data cleanup
- Investigate missing 5th section heading
- Full end-to-end testing in chat UI
- Verify section structure queries work in production interface

When implementing new features:
1. Follow the existing module structure
2. Add comprehensive error handling
3. Include proper logging
4. Write corresponding tests
5. Update documentation as needed
6. Ensure compatibility with existing Canvas integration
7. Consider section-aware processing for text-related features
