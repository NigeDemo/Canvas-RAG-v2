<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Canvas RAG v2 - Vision AI Integration

## Project Context
This is a Canvas RAG v2 system for architecture education that combines text and image content from Canvas LMS. The system is currently in Phase 2 completion, with vision AI capabilities for architectural drawing analysis fully implemented.

## Key Technical Details

### Architecture Stack
- **Backend**: Python with FastAPI/Streamlit
- **LLM Integration**: OpenAI GPT-4 (text + vision), Anthropic Claude (vision)
- **Vector Database**: ChromaDB for embeddings
- **Canvas Integration**: Canvas LMS API
- **Image Processing**: PIL, pdf2image, vision AI APIs

### Current Implementation Status
- **Phase 1 Complete**: Text indexing, basic image filename matching
- **Phase 2 Complete**: Vision AI integration for content analysis
- **Phase 3 Ready**: Performance optimization and BM25 integration

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

### Domain-Specific Context
- **Architecture Education**: Focus on construction drawings, plans, elevations, sections
- **Drawing Types**: Floor plans, site plans, elevations, details, perspectives
- **Technical Elements**: Dimensions, annotations, symbols, hatching patterns
- **Query Types**: Visual reasoning, measurement extraction, content identification

### File Structure
- `src/vision/` - Vision AI integration modules (✅ Complete)
- `src/generation/` - LLM integration and response generation
- `src/processing/` - Content processing including images
- `src/retrieval/` - Hybrid search and retrieval logic
- `src/indexing/` - Vector database operations

### Testing Strategy
- Unit tests for vision processing functions
- Integration tests for end-to-end vision queries
- Mock API responses for testing without API costs
- Visual regression testing for UI components

When implementing new features:
1. Follow the existing module structure
2. Add comprehensive error handling
3. Include proper logging
4. Write corresponding tests
5. Update documentation as needed
6. Ensure compatibility with existing Canvas integration
