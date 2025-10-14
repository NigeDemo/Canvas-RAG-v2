# Comprehensive Testing Plan - Canvas RAG v2

**Date**: October 3, 2025  
**Purpose**: Robust stress testing of all system capabilities  
**Context**: Student-facing tool for Canvas course content interaction  
**Priority**: CRITICAL - Core functionality verification needed

---

## 🔴 CRITICAL ISSUE: Image Retrieval Not Working

### Problem Discovered

**User Query**: "List all images from this canvas topic"

**System Response**:
```
"It appears that there are no images available from the Canvas course 
material provided, and no visual analysis has been performed. Therefore, 
I cannot list any images or provide a detailed insight into architectural 
drawings based on visual content from this specific topic."
```

Then provided generic architectural guidance instead of actual images.

### Why This Is Critical

**Intended Use Case**: Student-facing tool for Canvas course interaction
- Students need to **SEE** and **ACCESS** actual images/drawings from Canvas
- Images are core content for architecture course (plans, elevations, sections, details)
- Current behavior: Falls back to generic textbook content instead of course materials

**Impact**: Core feature (image retrieval) appears to be broken

---

## Testing Strategy

### Phase 1: Image Retrieval Testing (CRITICAL PRIORITY)

#### 1.1 Database Verification
**Goal**: Verify images are actually indexed

```bash
python check_database.py
```

**Check for**:
- [ ] `image_reference` content type exists
- [ ] Image URLs are stored in metadata
- [ ] Vision analysis data present (if applicable)
- [ ] Alt text and descriptions available
- [ ] Count of image references vs expected

**Diagnostic Query**:
```python
# Check image documents in database
results = collection.get(
    where={"content_type": "image_reference"},
    limit=100
)
print(f"Total image references: {len(results['ids'])}")
print(f"Sample image metadata: {results['metadatas'][0]}")
```

#### 1.2 Image Query Detection Testing
**Goal**: Verify system recognizes image-related queries

**Test Queries**:
```
1. "List all images from this canvas topic"
2. "Show me images about steel frames"
3. "What drawings are available?"
4. "Show me floor plan examples"
5. "Can you show me images of elevations?"
6. "What visual content is available?"
7. "Display all images from Session 5"
8. "Show me architectural drawings"
```

**Expected Behavior**:
- Query analyzer detects as visual/image query
- System searches for `content_type: image_reference`
- Returns list of actual images with URLs
- Includes image descriptions and metadata

**Check**:
- [ ] Query marked as `is_visual_query: true`
- [ ] Search includes image content types
- [ ] Results contain image metadata
- [ ] Response includes clickable URLs

#### 1.3 Image Retrieval Flow Testing
**Goal**: Trace complete image retrieval pipeline

**Test Script**:
```python
# test_image_retrieval.py
from src.indexing.vector_store import IndexBuilder
from src.retrieval.hybrid_search import HybridSearchEngine

# Initialize system
index_builder = IndexBuilder(embedding_model_type="openai")
retriever = index_builder.get_retriever()
search_engine = HybridSearchEngine(retriever)

# Test image query
query = "List all images from this Canvas topic"
results = search_engine.search(query, n_results=20)

# Analyze results
print(f"Total results: {results['total_results']}")
print(f"Query analysis: {results['query_analysis']}")

for i, result in enumerate(results['results'][:5]):
    print(f"\nResult {i+1}:")
    print(f"  Content type: {result.metadata.get('content_type')}")
    print(f"  Has image URL: {'image_url' in result.metadata}")
    print(f"  Has vision analysis: {'vision_analysis' in result.metadata}")
```

**Verify**:
- [ ] Query enhanced properly
- [ ] Retrieval returns image results
- [ ] Metadata includes image URLs
- [ ] Vision analysis present (if indexed)

#### 1.4 UI Image Display Testing
**Goal**: Verify images displayed in Streamlit UI

**Test in UI**:
1. Start app: `streamlit run src/ui/vision_chat_app.py`
2. Query: "List all images from Session 5"
3. **Expected**: List of images with:
   - Image descriptions
   - Clickable URLs to view images
   - Canvas source information
   - Vision analysis details (if available)

**Check**:
- [ ] Images listed in response
- [ ] URLs are clickable
- [ ] Images open in browser
- [ ] Metadata displayed correctly

---

### Phase 2: Module Query Testing

#### 2.1 Module Content Queries
**Test Queries**:
```
1. "What is covered in Session 5?"
2. "What's in the Session 4 module?"
3. "Tell me about Week 3"
4. "What documents are provided for Session 5?"
5. "What files are in Session 6?"
```

**Expected Behavior**:
- Detected as module query (intent: module_content)
- Enhanced with "Session X", "Module X", "Week X"
- Uses module_content template
- Explains Canvas structure
- Lists actual files and modules

**Verify**:
- [ ] No generic "likely covers" phrases
- [ ] Uses actual indexed content
- [ ] Mentions Canvas module names
- [ ] Lists real file names
- [ ] Explains prep materials location

#### 2.2 Module vs File Name Testing
**Test Queries**:
```
1. "What is in Session 5 module?" 
   (Should show: Model making + Session 6 prep materials)
   
2. "What is in Session 4 module?"
   (Should show: Steel Design + Session 5 prep materials)
```

**Verify**:
- [ ] Distinguishes module content from file names
- [ ] Explains where Session 5 files are located
- [ ] Mentions prep materials concept
- [ ] Shows actual file organization

---

### Phase 3: Content Retrieval Testing

#### 3.1 PDF Content Testing
**Test Queries**:
```
1. "What does the Light Steel Framing PDF cover?"
2. "Summarize Session 5 Steel Frame Design PDF"
3. "What's on page 1 of Light Steel Framing PDF?"
```

**Verify**:
- [ ] PDF content retrieved
- [ ] Page numbers cited
- [ ] Actual content (not hallucinations)
- [ ] Source metadata included

#### 3.2 PowerPoint Content Testing
**Test Queries**:
```
1. "What's covered in Steel Frame Design V2 PowerPoint?"
2. "Summarize slide 1 of Session 5 PowerPoint"
3. "What topics are in the steel frame presentation?"
```

**Verify**:
- [ ] PowerPoint content retrieved
- [ ] Slide numbers cited
- [ ] Slide text extracted
- [ ] Source metadata included

#### 3.3 Section Query Testing
**Test Queries**:
```
1. "What sections are on the Construction Drawing Package page?"
2. "What topics are covered on the drawing standards page?"
3. "What headings are on this page?"
```

**Verify**:
- [ ] Section headings detected
- [ ] Correct count (4-5 sections)
- [ ] Heading text accurate
- [ ] Section content summarized

---

### Phase 4: General Query Testing

#### 4.1 Factual Questions
**Test Queries**:
```
1. "How do I design steel frames?"
2. "What are the types of architectural drawings?"
3. "What is a floor plan?"
4. "Explain elevation drawings"
```

**Verify**:
- [ ] Uses indexed content (not hallucinations)
- [ ] Cites Canvas sources
- [ ] Practical architecture advice
- [ ] References course materials

#### 4.2 Visual Reasoning
**Test Queries**:
```
1. "Analyze this floor plan" (with image upload)
2. "What's shown in this drawing?"
3. "Identify the drawing type in this image"
```

**Verify**:
- [ ] Vision AI activates
- [ ] Image analyzed
- [ ] Architectural elements identified
- [ ] Technical details extracted

---

### Phase 5: Edge Case Testing

#### 5.1 Empty Results
**Test Queries**:
```
1. "Show me images about quantum physics"
2. "What is covered in Session 99?"
3. "List files from non-existent module"
```

**Expected**: Clear message about no content found

#### 5.2 Ambiguous Queries
**Test Queries**:
```
1. "Tell me about steel"
2. "What's covered?"
3. "Show me stuff"
```

**Expected**: Ask for clarification or provide general overview

#### 5.3 Mixed Queries
**Test Queries**:
```
1. "What images are in Session 5 about steel frames?"
2. "Show me floor plan images from the construction drawing page"
3. "What does the PowerPoint say about elevations and show me examples"
```

**Expected**: Handle multiple intent types, retrieve both text and images

---

## Testing Checklist

### Critical Tests (Must Pass)
- [ ] **Image list query returns actual images** (PRIORITY 1)
- [ ] **Image URLs are clickable and work**
- [ ] **Module queries use real content**
- [ ] **PDF content accessible**
- [ ] **PowerPoint content accessible**
- [ ] **No generic hallucinations**

### Important Tests (Should Pass)
- [ ] Section queries work
- [ ] Vision AI analyzes uploaded images
- [ ] Mixed queries handled
- [ ] Edge cases handled gracefully

### Optional Tests (Nice to Have)
- [ ] Query response time < 3 seconds
- [ ] Multiple queries in same session work
- [ ] Chat history maintained
- [ ] Source citations always present

---

## Diagnostic Tools

### 1. Database Inspector
```bash
python check_database.py
```
Shows: document count, content types, sample metadata

### 2. Image Retrieval Test
```bash
python test_image_retrieval.py  # (To be created)
```
Tests: image indexing, retrieval, metadata

### 3. Vision RAG Diagnostic
```bash
python test_vision_rag_session5.py
```
Tests: complete query flow, template selection, response generation

### 4. Module Query Test
```bash
python test_module_query_enhancement.py
```
Tests: module detection, query enhancement

---

## Success Criteria

### Minimum Viable (Must Have)
1. ✅ **Image queries return actual images from Canvas**
2. ✅ **Module queries return actual course content**
3. ✅ **PDF/PowerPoint content accessible**
4. ✅ **No generic hallucinations**
5. ✅ **Source citations always present**

### Full Feature Set (Should Have)
6. ✅ **Vision AI analyzes images**
7. ✅ **Section queries work**
8. ✅ **Mixed query types handled**
9. ✅ **Image URLs clickable**
10. ✅ **Canvas structure explained**

### Excellent User Experience (Nice to Have)
11. ✅ **Fast response times (< 3s)**
12. ✅ **Helpful error messages**
13. ✅ **Query suggestions**
14. ✅ **Image previews in UI**
15. ✅ **Conversation context maintained**

---

## Investigation Plan for Image Issue

### Step 1: Verify Image Indexing (5 minutes)
```bash
python check_database.py
```
Count image_reference documents, check metadata

### Step 2: Test Image Retrieval (5 minutes)
Create simple test script to query for images

### Step 3: Test UI Image Display (5 minutes)
Query in Streamlit UI, check response format

### Step 4: Identify Root Cause (10 minutes)
- Not indexed? → Check ingestion logs
- Not retrieved? → Check query detection
- Not displayed? → Check UI response formatting

### Step 5: Fix and Retest (varies)
Apply fix, rerun tests, verify working

---

## Expected Outcomes

### After Testing
1. **Image retrieval issue identified and fixed**
2. **All core features verified working**
3. **Edge cases documented**
4. **Student-facing tool ready for use**

### Documentation Updates
1. **Known issues list** (if any remain)
2. **Usage examples** for students
3. **Query patterns guide**
4. **Troubleshooting guide**

---

## Timeline Estimate

### Phase 1: Image Testing (CRITICAL)
- Database check: 5 minutes
- Retrieval testing: 10 minutes
- UI testing: 10 minutes
- Fix (if needed): 30-60 minutes
- **Total**: ~1 hour

### Phase 2: Module Testing
- Query testing: 15 minutes
- Verification: 10 minutes
- **Total**: 25 minutes

### Phase 3: Content Testing
- PDF/PowerPoint: 15 minutes
- Section queries: 10 minutes
- **Total**: 25 minutes

### Phase 4: General Testing
- Various queries: 20 minutes
- **Total**: 20 minutes

### Phase 5: Edge Cases
- Testing: 15 minutes
- **Total**: 15 minutes

**Grand Total**: ~2 hours for comprehensive testing

---

## Notes for Next Session

### Priority Order
1. 🔴 **Fix image retrieval** (CRITICAL - students need images!)
2. 🟡 **Verify module queries** (seems fixed, quick test)
3. 🟢 **Test other features** (comprehensive validation)

### Remember
- This is a **student-facing tool**
- Students need to **interact with actual Canvas content**
- Images/drawings are **core architecture course content**
- Generic textbook content is **NOT acceptable**

### Success = Students Can:
- ✅ List all images from a topic
- ✅ View architectural drawings
- ✅ Access PDF/PowerPoint content
- ✅ Navigate course modules
- ✅ Get answers from actual course materials

---

**Status**: Ready for comprehensive testing  
**Priority**: Image retrieval (CRITICAL)  
**Estimated Time**: 2 hours for full test suite  
**Success Criteria**: All 5 minimum viable features working
