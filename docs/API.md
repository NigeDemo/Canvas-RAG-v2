# Canvas RAG v2 - API Documentation

## System Architecture

The Canvas RAG v2 system is built with a modular architecture that supports multimodal content processing, vision AI integration, and hybrid retrieval:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Canvas API    │───▶│   Data Pipeline  │───▶│   Vector Store  │
│                 │    │                  │    │   (ChromaDB)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Chat Interface │◀───│  RAG Pipeline    │◀───│ Hybrid Retrieval│
│  (Streamlit)    │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │   LLM Response   │    │   Vision AI     │
                    │  (GPT-4/Gemini)  │    │ (GPT-4 Vision)  │
                    └──────────────────┘    └─────────────────┘
```

## Core Components

### 1. Data Ingestion (`src.ingestion`)

**CanvasIngester**: Handles fetching content from Canvas LMS
- Connects to Canvas API using token authentication
- Downloads pages (HTML content)
- Downloads files (PDFs, images)
- Preserves metadata and source links

```python
from src.ingestion import CanvasIngester

async with CanvasIngester() as ingester:
    metadata = await ingester.ingest_course_content("course_id")
```

### 2. Content Processing (`src.processing`)

**ContentProcessor**: Converts raw content into structured segments
- Extracts text from HTML pages
- Converts PDFs to images with text extraction
- Processes standalone images
- Creates chunks with metadata for indexing

```python
from src.processing import ContentProcessor

processor = ContentProcessor()
segments = processor.process_course_content(metadata_path)
```

### 3. Embeddings (`src.embeddings`)

**EmbeddingManager**: Handles multimodal embeddings
- Supports Nomic Embed Multimodal (recommended)
- Fallback to OpenAI text embeddings
- Combines text and visual content for embeddings

```python
from src.embeddings import EmbeddingManager

embedding_manager = EmbeddingManager(model_type="nomic")
embeddings = embedding_manager.embed_content(content_segments)
```

### 4. Indexing (`src.indexing`)

**VectorStore**: ChromaDB-based vector storage
- Persistent storage of embeddings
- Metadata filtering capabilities
- Cosine similarity search

**SparseIndex**: BM25-based keyword search
- Traditional keyword matching
- Domain-specific term matching
- Complements dense retrieval

**HybridRetriever**: Combines dense and sparse search
- Reciprocal Rank Fusion (RRF)
- Configurable fusion weights
- Result ranking and scoring

```python
from src.indexing import IndexBuilder

index_builder = IndexBuilder()
index_builder.build_index(processed_content_path)
retriever = index_builder.get_retriever()
```

### 5. Retrieval (`src.retrieval`)

**HybridSearchEngine**: Orchestrates search and ranking
- Query analysis and intent detection
- Result processing and highlighting
- Source grouping and ranking

```python
from src.retrieval import HybridSearchEngine

search_engine = HybridSearchEngine(retriever)
results = search_engine.search("What scale for floor plans?")
```

### 6. Generation (`src.generation`)

**RAGPipeline**: Complete question-answering pipeline
- Context formatting from search results
- Prompt engineering for different query types
- LLM integration (OpenAI GPT-4, Google Gemini)
- Response generation with citations

```python
from src.generation import RAGPipeline

rag_pipeline = RAGPipeline(search_engine, llm_provider_type="openai")
response = rag_pipeline.query("How should dimension lines be placed?")
```

## Query Types and Prompting

The system supports different types of architectural queries:

### 1. Factual Queries
Questions about facts, standards, or procedures.
- Example: "What scale should I use for a site plan?"
- Uses factual prompt template
- Focuses on precise, technical answers

### 2. Visual Reasoning Queries  
Questions about visual elements in drawings.
- Example: "What drawing shows perspective section details?"
- Uses visual reasoning prompt template
- Processes images and visual content
- Describes visual elements

### 3. Measurement/Scale Queries
Questions about dimensions, scales, and measurements.
- Example: "What are standard scales for architectural drawings?"
- Uses measurement prompt template
- Emphasizes technical standards

### 4. General Queries
Catch-all for other questions.
- Uses general prompt template
- Flexible response format

## Configuration

### Environment Variables

Required variables in `.env`:

```bash
# Canvas LMS Configuration
CANVAS_API_URL=https://your-institution.instructure.com
CANVAS_API_TOKEN=your_canvas_api_token
CANVAS_COURSE_ID=your_course_id

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-vision-preview

# Retrieval Configuration
DENSE_RETRIEVAL_TOP_K=10
SPARSE_RETRIEVAL_TOP_K=10
HYBRID_FUSION_ALPHA=0.5

# Processing Configuration
PDF_DPI=200
MAX_IMAGE_SIZE=1024
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### System Settings

Accessible via `src.config.settings`:

```python
from src.config.settings import settings

print(f"Embedding model: {settings.openai_model}")
print(f"Fusion alpha: {settings.hybrid_fusion_alpha}")
```

## API Reference

### Core Classes

#### CanvasIngester
```python
class CanvasIngester:
    async def ingest_course_content(course_id: str) -> Dict[str, Any]
    def get_pages(course: Course) -> List[Page]
    def get_files(course: Course) -> List[File]
    async def download_file(file: File, download_dir: Path) -> Optional[Path]
```

#### ContentProcessor
```python
class ContentProcessor:
    def process_pdf(pdf_path: Path) -> List[Dict[str, Any]]
    def process_image(image_path: Path) -> Optional[Dict[str, Any]]
    def extract_html_content(html_content: str) -> Dict[str, Any]
    def chunk_text(text: str, metadata: Dict = None) -> List[Dict[str, Any]]
```

#### HybridRetriever
```python
class HybridRetriever:
    def retrieve(query: str, n_results: int = 10) -> List[Dict[str, Any]]
    def reciprocal_rank_fusion(dense_results, sparse_results) -> List[Tuple[int, float]]
```

#### RAGPipeline
```python
class RAGPipeline:
    def query(user_query: str, n_results: int = 10) -> Dict[str, Any]
```

## Error Handling

The system includes comprehensive error handling:

- **Connection errors**: Canvas API timeouts, authentication failures
- **Processing errors**: Corrupted PDFs, unsupported image formats
- **Embedding errors**: Model failures, rate limits
- **Search errors**: Empty results, indexing issues
- **Generation errors**: LLM failures, prompt issues

All errors are logged using the configured logger and graceful fallbacks are provided.

## Performance Considerations

### Embedding Generation
- Batch processing for efficiency
- Caching of embeddings
- Configurable model selection

### Vector Search
- Persistent ChromaDB storage
- Optimized similarity search
- Metadata filtering support

### Memory Usage
- Streaming file processing
- Configurable chunk sizes
- Image resize limits

### Response Time
- Parallel dense/sparse search
- Result caching
- Optimized prompt templates

## Security

### API Keys
- Environment variable storage
- No hardcoded credentials
- Secure token handling

### Data Privacy
- Local storage by default
- No data sent to external services (except LLM APIs)
- Canvas permissions respected

### Access Control
- Canvas token permissions
- Course-level access control
- User authentication via Canvas

## Troubleshooting

### Common Issues

1. **No results found**
   - Check if content was ingested properly
   - Verify embedding model is working
   - Review query phrasing

2. **Canvas API errors**
   - Verify API token permissions
   - Check Canvas URL format
   - Confirm course access

3. **Embedding failures**
   - Check API key validity
   - Verify model availability
   - Review rate limits

4. **PDF processing errors**
   - Install poppler utilities
   - Check PDF format support
   - Verify file permissions

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

Check logs in `logs/canvas_rag.log` for detailed error information.
