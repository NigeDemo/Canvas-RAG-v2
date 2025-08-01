# Next Session Task List - Fresh Start & Complete Testing

## 🎯 Session Goals
Complete fresh pipeline run and end-to-end testing of section-aware architecture in chat UI.

## 📋 Step-by-Step Tasks

### 1. Clean Slate Setup
```bash
# Clear all existing data (simplified after repo cleanup)
rm -rf data/processed/* data/chroma_db/* data/cache/*

# Verify clean state
python debug_db.py  # Should show empty database
```

### 2. Fresh Pipeline Run
```bash
# Run complete pipeline from scratch
python scripts/run_pipeline.py --course-id 45166 --page-url construction-drawing-package-2

# Monitor section detection output
# Look for: "Extracted X sections from text"
# Expected: Should find 5 sections, currently only finding 4
```

### 3. Section Detection Investigation
**Current Issue**: Only 4/5 section headings detected

**Tasks**:
- Check original Canvas page for all 5 section headings
- Review section detection patterns in `src/processing/content_processor.py`
- Debug which heading is missing and why
- Fix detection logic if needed

### 4. Indexing Verification
```bash
# Verify indexing completed successfully
python check_section_headings.py

# Expected output:
# - 5 section headings (not 4)
# - Proper metadata for each heading
# - Correct section_index numbering
```

### 5. Chat UI Testing
```bash
# Start chat interface
streamlit run src/ui/vision_chat_app.py

# Test section queries:
# 1. "What sections are on this page?"
# 2. "What are the main headings?"
# 3. "List the sections covered"

# Expected: Should return all 5 section headings, not general content
```

### 6. End-to-End Validation
**Section Queries**:
- Test in chat UI (not just command line)
- Verify correct section headings returned
- Check that general content isn't returned instead

**Vision Queries**:
- Test architectural drawing analysis
- Verify image retrieval and description

**Hybrid Queries**:
- Test combination of text + image content

## 🔍 Debugging Areas

### Missing Section Heading
**Potential Issues**:
- Section heading pattern not matching
- Text processing fragmenting the heading
- Different format/punctuation than expected
- Hidden characters or encoding issues

**Debug Commands**:
```bash
# Check raw Canvas content (if needed, use main pipeline with debug flag)
python scripts/run_pipeline.py --course-id 45166 --page-url construction-drawing-package-2 --debug

# Check section detection (main debug tool)
python check_section_headings.py

# Database inspection
python debug_db.py
```

### Chat UI Integration
**Verify**:
- HybridRetriever properly initialized
- Section query detection working
- Section heading prioritization functioning
- Results properly formatted for UI

## 📊 Success Criteria

### Fresh Pipeline
- ✅ Clean database successfully created
- ✅ All 5 section headings detected and indexed
- ✅ 87+ documents in ChromaDB with proper metadata
- ✅ Section-aware chunks properly created

### Chat UI Testing
- ✅ "What sections are on this page?" returns 5 headings
- ✅ Section headings listed, not general content
- ✅ Vision queries work for architectural drawings
- ✅ No errors in Streamlit interface

### System Integration
- ✅ OpenAI embeddings working with rate limiting
- ✅ BM25 sparse retrieval functional
- ✅ Section prioritization working in chat UI
- ✅ Complete end-to-end functionality verified

## 🚫 Known Issues to Address

1. **Missing 5th Section**: Currently only detecting 4/5 headings
2. **Chat UI Testing Gap**: Section queries tested in CLI but not UI
3. **Pipeline Freshness**: Current data may have inconsistencies from iterative fixes

## 📝 Next Session Notes

- Start with complete data wipe
- Focus on finding missing section heading
- Prioritize chat UI testing over command line testing
- Document any new issues found
- Ensure production-ready state by session end

---

**Goal**: Complete, tested, production-ready Canvas RAG v2 with verified section-aware architecture working in the actual chat interface.
