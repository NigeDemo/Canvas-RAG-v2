# Changelog

All notable changes to Canvas RAG v2 will be documented in this file.

## [2.0.1] - 2025-10-14 - Docs tidy-up + image UX + smoke test

### Added
- Scripts: `scripts/smoke_test_images.py` to quickly validate image queries end-to-end

### Changed
- UI: Improved image label fallback in `src/ui/vision_chat_app.py` (alt_text → page_title (+content_type) → filename → "Canvas image"), plus contextual details (module | page | filename | type)
- Docs: Centralized documentation index at `docs/README.md` and moved historical/superseded root docs to `docs/archive/`

### Fixed/Verified
- Retrieval: Image-first hybrid retrieval verified via smoke test; vision cache hit paths confirmed
- Sparse retrieval: BM25 auto-population active (logs show 479 text docs) and used in hybrid search

### Maintenance
- Removed duplicated historical Markdown files from repo root (archived copies preserved under `docs/archive/`)

## [2.0.0] - 2025-07-17 - Phase 2 Complete ✅

### Added
- **Vision AI Integration**: GPT-4 Vision and Claude Vision API support
- **Architectural Drawing Analysis**: Detailed analysis of electrical plans, elevations, sections
- **OCR Capabilities**: Text extraction from architectural drawings
- **Vision-Enhanced Chat Interface**: New Streamlit app with vision capabilities
- **Intelligent Caching**: Vision analysis result caching to minimize API costs
- **Multiple Analysis Types**: Comprehensive, spatial, technical, OCR analysis options
- **Enhanced Image Processing**: Specialized handling for architectural drawings

### Changed
- **Primary Interface**: Moved to `src/ui/vision_chat_app.py` for vision-enhanced experience
- **Query Processing**: Added vision AI integration for image-related queries
- **Response Generation**: Enhanced with actual visual analysis instead of filename matching
- **Project Structure**: Organized into professional directories (debug/, tests/, setup/)

### Fixed
- **Image Reference Extraction**: Fixed dictionary format handling from HybridSearchEngine
- **Vision AI Pipeline**: Resolved generic response issue with electrical plan queries
- **Project Organization**: Cleaned up development artifacts for GitHub deployment

### Technical Notes
- **Phase 2 Complete**: Vision AI integration fully functional
- **Vision Providers**: GPT-4 Vision (primary), Claude Vision (fallback)
- **Analysis Capabilities**: 4000+ character detailed responses for architectural drawings
- **Caching System**: Efficient result caching to avoid redundant API calls

## [1.0.0] - 2025-07-03 - Phase 1 Complete

### Added
- LLM-powered response generation using GPT-4
- Enhanced image query detection with keyword and phrase matching
- Improved system prompts for architectural drawing assistance
- Debug interface in Streamlit chat app
- Clickable markdown links for image references
- Enhanced image retrieval prioritization for visual queries

### Changed
- Switched from basic search result concatenation to intelligent LLM synthesis
- Improved user prompts to explicitly instruct LLM about image capabilities
- Enhanced error handling and logging throughout the chat application
- Updated query detection to handle more natural language patterns

### Fixed
- Image references now properly included in LLM context
- Circular reference issue in enhanced image query fallback
- Proper URL formatting in LLM responses
- Image query detection edge cases

### Technical Notes
- Currently using OpenAI text-embedding-3-large (not multimodal embeddings)
- BM25 sparse retrieval not currently active (initialization issues)
- Images are referenced by filename/URL only (no visual content analysis)
- System stores image metadata but does not analyze visual content

## [1.0.0] - Initial Implementation

### Added
- Canvas LMS API integration
- Basic content processing and chunking
- ChromaDB vector storage
- Streamlit chat interface
- Single page and full course ingestion
- Image reference extraction from HTML content
