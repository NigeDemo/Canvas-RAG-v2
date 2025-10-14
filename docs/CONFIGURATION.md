# Configuration Guide - Canvas RAG v2

## Quick Start

1. **Copy the example environment file:**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit `.env` with your values:**
   - Canvas API credentials
   - OpenAI API key
   - Page URLs for multi-page processing

3. **Run the pipeline:**
   ```powershell
   python scripts/run_multi_page_pipeline.py
   ```

---

## Configuration Files

### `.env` - Environment Variables
**Location:** Project root  
**Purpose:** Store API keys, credentials, and configuration  
**⚠️ Important:** Never commit `.env` to Git (already in `.gitignore`)

### `.env.example` - Template
**Location:** Project root  
**Purpose:** Template showing all available settings  
**✅ Safe to commit:** Contains no actual secrets

---

## Essential Configuration

### Canvas LMS Settings

```bash
# Your Canvas instance URL
CANVAS_API_URL=https://canvas.instructure.com

# Your Canvas API token
# Get this from: Canvas → Account → Settings → New Access Token
CANVAS_API_TOKEN=your_token_here

# Default course ID for single-page pipeline
CANVAS_COURSE_ID=45166
```

**Finding Your Course ID:**
1. Go to your Canvas course
2. Look at the URL: `https://canvas.example.com/courses/45166`
3. The number after `/courses/` is your course ID

### Multi-Page Pipeline Settings

```bash
# Comma-separated list of page URL slugs
CANVAS_MULTI_PAGE_URLS=home,syllabus,modules,construction-drawing-package-2
```

**Finding Page URL Slugs:**
1. Navigate to a Canvas page
2. Look at the URL: `https://canvas.example.com/courses/45166/pages/construction-drawing-package-2`
3. The slug is the last part: `construction-drawing-package-2`
4. List multiple pages separated by commas (no spaces)

**Examples:**
```bash
# Two pages
CANVAS_MULTI_PAGE_URLS=home,syllabus

# Four pages (current example)
CANVAS_MULTI_PAGE_URLS=home,syllabus,modules,construction-drawing-package-2

# Many pages
CANVAS_MULTI_PAGE_URLS=page1,page2,page3,page4,page5
```

### OpenAI Settings

```bash
# Your OpenAI API key
# Get this from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...your_key_here

# Models to use
OPENAI_MODEL=gpt-4-vision-preview
OPENAI_VISION_MODEL=gpt-4o
```

### Anthropic Settings (Optional - for Vision AI)

```bash
# Your Anthropic API key
# Get this from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-...your_key_here

# Claude model
CLAUDE_VISION_MODEL=claude-3-5-sonnet-20241022
```

---

## Advanced Configuration

### Vision AI Settings

```bash
# Which provider to try first for vision analysis
VISION_PRIMARY_PROVIDER=openai
# Options: openai, claude

# Fallback if primary fails
VISION_FALLBACK_PROVIDER=claude
# Options: openai, claude

# Enable caching to save API costs
VISION_CACHE_ENABLED=true

# Cache expiration (hours)
VISION_CACHE_TTL_HOURS=24
```

### Retrieval Settings

```bash
# Number of results from vector search
DENSE_RETRIEVAL_TOP_K=10

# Number of results from BM25 search
SPARSE_RETRIEVAL_TOP_K=10

# Fusion weight (0.5 = equal weight to vector and BM25)
HYBRID_FUSION_ALPHA=0.5

# Final number of results after re-ranking
RERANK_TOP_K=5
```

### Query Enhancement Settings

```bash
# Enable intelligent query expansion
ENABLE_QUERY_ENHANCEMENT=true

# Maximum synonym terms to add
QUERY_ENHANCEMENT_MAX_TERMS=10

# Show enhancement in logs
QUERY_ENHANCEMENT_DEBUG=true
```

### Processing Settings

```bash
# PDF conversion quality
PDF_DPI=200

# Maximum image dimension (pixels)
MAX_IMAGE_SIZE=1024

# Text chunking size (tokens)
CHUNK_SIZE=512

# Overlap between chunks (tokens)
CHUNK_OVERLAP=50
```

### Database Settings

```bash
# ChromaDB storage location
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Collection name
CHROMA_COLLECTION_NAME=canvas_multimodal
```

### Logging Settings

```bash
# Log level
LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR

# Log file location
LOG_FILE=./logs/canvas_rag.log
```

---

## Configuration for Different Use Cases

### Use Case 1: Development (Local Testing)

```bash
# Minimal setup for testing
CANVAS_API_URL=https://canvas.instructure.com
CANVAS_API_TOKEN=your_token
CANVAS_COURSE_ID=45166
OPENAI_API_KEY=your_key

# Process just 1-2 pages
CANVAS_MULTI_PAGE_URLS=home,construction-drawing-package-2

# Enable debug logging
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

### Use Case 2: Production (Full Course)

```bash
# Full production setup
CANVAS_API_URL=https://canvas.instructure.com
CANVAS_API_TOKEN=your_production_token
CANVAS_COURSE_ID=45166

# Process all important pages
CANVAS_MULTI_PAGE_URLS=home,syllabus,modules,assignments,resources

# Both vision providers
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Optimize for quality
RERANK_TOP_K=10
VISION_CACHE_ENABLED=true

# Production logging
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Use Case 3: Cost-Conscious (API Limits)

```bash
# Basic setup
CANVAS_API_URL=https://canvas.instructure.com
CANVAS_API_TOKEN=your_token
CANVAS_COURSE_ID=45166
OPENAI_API_KEY=your_key

# Limit pages
CANVAS_MULTI_PAGE_URLS=home,syllabus

# Disable vision AI to save costs
VISION_PRIMARY_PROVIDER=none

# Reduce retrieval
DENSE_RETRIEVAL_TOP_K=5
SPARSE_RETRIEVAL_TOP_K=5
RERANK_TOP_K=3

# Aggressive caching
VISION_CACHE_ENABLED=true
VISION_CACHE_TTL_HOURS=168  # 1 week
```

---

## Validation

### Check Your Configuration

Run this to verify settings are loaded:

```powershell
python -c "from src.config.settings import settings; print(f'Course ID: {settings.canvas_course_id}'); print(f'Pages: {settings.multi_page_urls_list}')"
```

Expected output:
```
Course ID: 45166
Pages: ['home', 'syllabus', 'modules', 'construction-drawing-package-2']
```

### Common Issues

**Issue: Settings not loading**
- Check `.env` file is in project root
- Check syntax (no quotes around values needed)
- Check for typos in variable names

**Issue: API errors**
- Verify API keys are valid
- Check API key permissions
- Test keys in Canvas/OpenAI dashboards

**Issue: Empty page list**
- Verify `CANVAS_MULTI_PAGE_URLS` is set
- Check for proper comma separation
- Ensure no trailing commas

---

## Security Best Practices

### ✅ DO:
- Use `.env` for all secrets
- Keep `.env` out of Git (check `.gitignore`)
- Use separate `.env` files for dev/prod
- Rotate API keys regularly
- Use read-only Canvas tokens when possible

### ❌ DON'T:
- Commit `.env` to Git
- Hard-code API keys in scripts
- Share `.env` files via email/chat
- Use production keys in development
- Store keys in code comments

---

## Environment Files Checklist

- [ ] Copied `.env.example` to `.env`
- [ ] Set `CANVAS_API_URL`
- [ ] Set `CANVAS_API_TOKEN`
- [ ] Set `CANVAS_COURSE_ID`
- [ ] Set `CANVAS_MULTI_PAGE_URLS`
- [ ] Set `OPENAI_API_KEY`
- [ ] (Optional) Set `ANTHROPIC_API_KEY`
- [ ] Verified `.env` is in `.gitignore`
- [ ] Tested configuration loads correctly

---

**Ready to run?**

```powershell
python scripts/run_multi_page_pipeline.py
```

For more details, see: `docs/MULTI_PAGE_INGESTION.md`
