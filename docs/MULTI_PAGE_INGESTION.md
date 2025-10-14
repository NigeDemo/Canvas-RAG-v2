# Multi-Page Canvas Pipeline Guide

## Overview

This guide explains how to process multiple Canvas pages (or a full course) using the RAG system pipeline.

## Architecture Clarification

### Pipeline Scripts### Issue: Old data interfering

**Solution:** Clear and rebuild from scratch:

```powershell
# This will backup and clear your database
python scripts/clear_database.py

# Then re-run pipeline
python scripts/run_multi_page_pipeline.py
```

### Issue: Want to restore a backup

**Solution:** Restore from timestamped backup:

```powershell
# List available backups
Get-ChildItem data/chroma_db_backups/

# Restore a specific backup
Remove-Item data/chroma_db -Recurse
Copy-Item data/chroma_db_backups/chroma_db_backup_20251002_122000 data/chroma_db -Recurse
```s)
These scripts run the complete pipeline: Ingestion → Processing → Indexing

- **`scripts/run_pipeline.py`** - Single page or full course
  - Uses: `--page-url` for single page
  - Uses: `--course-id` for full course
  
- **`scripts/run_multi_page_pipeline.py`** - Multiple specific pages (NEW)
  - Batch processes multiple pages you specify
  - Consolidates all content before indexing

### Core Modules (Used by Pipeline Scripts)
- **`src/ingestion/canvas_ingester.py`** - Canvas API interaction
- **`src/processing/content_processor.py`** - Content processing with section-aware chunking
- **`src/indexing/vector_store.py`** - Vector and BM25 indexing

## Problem with Sequential Processing

**Don't do this:**
```powershell
# ❌ This will work for Vector store but BM25 will only index the LAST page
python scripts/run_pipeline.py --page-url "home"
python scripts/run_pipeline.py --page-url "syllabus"
python scripts/run_pipeline.py --page-url "modules"
```

**Why?** Because:
- ✅ Vector store (ChromaDB) **accumulates** documents (good!)
- ❌ BM25 index is **rebuilt** each time using only the latest processed file (bad!)

## Solution: Batch Processing with Multi-Page Pipeline

Use the `run_multi_page_pipeline.py` script to process all pages together.

### Method 1: Multi-Page Pipeline (Recommended for Specific Pages)

**Step 1: Configure pages in .env file**

Edit your `.env` file and add:

```bash
# Canvas course ID
CANVAS_COURSE_ID=45166

# Comma-separated list of page URL slugs
CANVAS_MULTI_PAGE_URLS=home,syllabus,modules,construction-drawing-package-2
```

**Finding Page URL Slugs:**
- The slug is the last part of your Canvas page URL
- Example: `https://canvas.example.com/courses/45166/pages/construction-drawing-package-2`
- Slug: `construction-drawing-package-2`

**Step 2: Clear existing database (recommended)**

If you have existing data and want a clean start:

```powershell
python scripts/clear_database.py
```

This will:
- ✅ Create a timestamped backup of your current database
- ✅ Clear the vector database to prevent duplicates
- ✅ Clear processed data files
- ✅ Keep your raw ingested data safe

**Step 3: Run the pipeline**

```powershell
python scripts/run_multi_page_pipeline.py
```

This will:
1. ✅ Read page URLs from your `.env` file
2. ✅ Ingest all specified pages from Canvas (uses `CanvasIngester`)
3. ✅ Process all pages with section-aware chunking (uses `ContentProcessor`)
4. ✅ Consolidate into single dataset
5. ✅ Build both Vector and BM25 indices with ALL content (uses `IndexBuilder`)

### Method 2: Full Course Pipeline (All Pages at Once)

To ingest the **entire course** (all pages):

```powershell
python scripts/run_pipeline.py --course-id 45166
```

This will:
- Get ALL pages from the course
- Download ALL files (PDFs, images)
- Process everything at once
- Build complete indices

**Warning:** This may take a long time and use significant API quota if the course has many pages!

## What Happens

### File Structure After Ingestion

```
data/
  raw/
    page_home_metadata.json
    page_syllabus_metadata.json
    page_modules_metadata.json
    page_construction_drawing_package_2_metadata.json
    files/
      [downloaded images and PDFs]
      
  processed/
    processed_page_home_metadata.json
    processed_page_syllabus_metadata.json
    processed_page_modules_metadata.json
    processed_page_construction_drawing_package_2_metadata.json
    processed_multi_page_consolidated.json  ← This is used for indexing
    
  chroma_db/
    [Vector database with all content]
```

### Database Statistics

After processing 4 pages, you can expect:
- **Vector Database**: 200-500 documents (depending on page content)
- **BM25 Index**: 80-200 text documents
- **Section Headings**: 20-50 section structure items
- **Image References**: 10-30 images (if present)

## Verifying the Results

### Check Database Contents

```powershell
python check_database.py
```

Expected output:
```
Database Statistics:
Collection: canvas_multimodal
Total Documents: 347

Sample Document:
ID: abc-123-def
Type: section_content
Text: [content preview...]
Source: construction drawing package
```

### Test Queries

Start the Streamlit app and try:

```
1. "What is the syllabus for this course?"
2. "What modules are covered?"
3. "Explain construction drawings"
4. "What sections are on the home page?"
```

All queries should now work across all ingested pages!

## Current vs New Coverage

### Before (Single Page Only):
- Pages: 1 (construction-drawing-package-2)
- Documents: 87
- BM25 Index: 28 text documents
- Coverage: Only answers questions about construction drawing packages

### After (4 Pages):
- Pages: 4 (home, syllabus, modules, construction-drawing-package-2)
- Documents: ~347 (estimated)
- BM25 Index: ~120 text documents (estimated)
- Coverage: Can answer questions about:
  - Course overview and objectives (home)
  - Course schedule and requirements (syllabus)
  - Learning modules and topics (modules)
  - Technical drawing details (construction-drawing-package-2)

## Troubleshooting

### Issue: "CANVAS_COURSE_ID is required"

**Solution:** Add the course ID to your `.env` file:
```bash
CANVAS_COURSE_ID=45166
```

### Issue: "CANVAS_MULTI_PAGE_URLS is required"

**Solution:** Add comma-separated page URLs to your `.env` file:
```bash
CANVAS_MULTI_PAGE_URLS=home,syllabus,modules,construction-drawing-package-2
```

### Issue: "No page metadata files found"

**Solution:** Check that ingestion completed successfully. Look for `page_*_metadata.json` files in `data/raw/`.

### Issue: API rate limit errors

**Solution:** Canvas API has rate limits. If you hit them:
1. Wait a few minutes
2. Process pages in smaller batches
3. Use `--skip-ingestion` flag to skip already-ingested pages

### Issue: Old data interfering

**Solution:** Clear and rebuild from scratch:

```powershell
# Backup current data
Move-Item data/chroma_db data/chroma_db_backup

# Clear processed files
Remove-Item data/processed/*.json

# Re-run pipeline
python scripts/ingest_multiple_pages.py
```

## Performance Considerations

### Time Estimates
- **Ingestion**: ~10-30 seconds per page (depends on size and images)
- **Processing**: ~5-15 seconds per page
- **Indexing**: ~30-60 seconds for all pages combined
- **Total**: 2-5 minutes for 4 pages

### API Quota Usage
- **Canvas API**: ~1-5 requests per page
- **OpenAI Embeddings**: 1 request per chunk (~200 chunks for 4 pages)
- **Vision AI**: 0-3 requests per image (if enabled during processing)

### Storage Requirements
- **Raw data**: ~50-200 KB per page
- **Processed data**: ~100-500 KB per page
- **Vector DB**: ~5-10 MB for 4 pages
- **Total**: ~20-30 MB for complete 4-page dataset

## Next Steps

After successful multi-page ingestion:

1. ✅ Test queries in Streamlit chat interface
2. ✅ Verify hybrid retrieval shows results from all pages
3. ✅ Check logs for BM25 document counts
4. 📊 Consider adding more pages if needed
5. 🚀 Move to Phase 3 Task 2 (Performance Optimization)

---

**Ready to process multiple pages?** 

1. **Configure your `.env` file:**
   ```bash
   CANVAS_COURSE_ID=45166
   CANVAS_MULTI_PAGE_URLS=home,syllabus,modules,construction-drawing-package-2
   ```

2. **Clear existing database (recommended):**
   ```powershell
   python scripts/clear_database.py
   ```

3. **Run the pipeline:**
   ```powershell
   python scripts/run_multi_page_pipeline.py
   ```

For detailed configuration guide, see: `docs/CONFIGURATION.md`

## File Organization Summary

```
scripts/                          ← Pipeline orchestrators
  ├── run_pipeline.py            ← Single page or full course
  ├── run_multi_page_pipeline.py ← Multiple specific pages (batch)
  ├── rebuild_index.py           ← Rebuild indices from existing processed data
  ├── demo_single_page.py        ← Demo/testing script
  └── quick_start.py             ← Initial setup script

src/
  ├── ingestion/                 ← Core modules (used by pipeline scripts)
  │   └── canvas_ingester.py    ← Canvas API interaction
  ├── processing/
  │   └── content_processor.py  ← Content processing & chunking
  ├── indexing/
  │   └── vector_store.py       ← Vector & BM25 indexing
  └── ...
```

**Key Principle:** 
- **Pipeline scripts** = Orchestrators that call core modules
- **Core modules** = Reusable components for Canvas, processing, indexing

