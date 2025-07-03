# Changelog

All notable changes to Canvas RAG v2 will be documented in this file.

## [Unreleased] - 2025-07-03

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
