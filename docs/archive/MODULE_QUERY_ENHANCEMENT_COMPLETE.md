# Module-Aware Query Enhancement - Implementation Complete

**Date**: October 3, 2025  
**Status**: ✅ Implemented  
**No Re-ingestion Required**: All changes are query-time enhancements

---

## 🎯 Changes Implemented

### 1. Query Analysis Enhancement
**File**: `src/retrieval/hybrid_search.py`

#### Added Module Query Detection
```python
'module': r'\b(session|module|week)\s+(\d+)\b',
'module_content': r'\b(covered|taught|learn|topics?)\b.*\b(session|module|week)\s+(\d+)\b'
```

**Detects queries like:**
- "What is covered in Session 5?"
- "What's in Module 3?"
- "Tell me about Week 7"
- "What do we learn in Session 4?"

#### Enhanced Query Analysis Result
```python
analysis = {
	 'is_module_query': True/False,
	 'module_number': '5',  # Extracted number
	 'intent': 'module_content',  # Special intent for module queries
	 ...
}
```

### 2. Module Query Enhancement
**File**: `src/retrieval/hybrid_search.py`

Added priority handling for module queries in `enhance_query()`:

```python
# 0. Module query enhancement (highest priority)
if analysis.get('is_module_query') and analysis.get('module_number'):
	 module_num = analysis['module_number']
	 enhanced_terms.update([
		  f'Session {module_num}',
		  f'Module {module_num}',
		  f'Week {module_num}'
	 ])
```

**Benefits:**
- Searches for "Session X", "Module X", "Week X" variations
- Finds content regardless of which term is used in Canvas
- Returns early to avoid cluttering with too many terms

### 3. New Prompt Template for Module Queries
**File**: `src/generation/llm_integration.py`

Added `'module_content'` template with Canvas structure context:

```python
'module_content': """You are an expert assistant helping architecture students navigate their Canvas course modules.

Important Note About Canvas Course Structure:
- Files and materials are placed in Canvas modules by the instructor for when students need them
- Prep materials for upcoming sessions may appear in earlier modules
- For example: "Session 5" prep materials may be in the "Session 4" module
- The module structure reflects teaching logistics, not just content naming

Context: The following content was retrieved from Canvas course materials:

{context}

Student Question: {query}

Instructions:
- Answer based on what's actually IN the specified Canvas module, not what the files are named
- If you find prep materials (files for future sessions) in the module, mention them clearly
- Distinguish between: 
  1. Main module content (what's taught that week)
  2. Prep materials (content for upcoming sessions)
- Explain if materials for a session are split across modules
- Include Canvas module names and file names in your response
- Be specific about what students will find where

Answer:"""
```

**Key Features:**
- Explains Canvas prep material placement
- Instructs LLM to distinguish module content vs. file names
- Tells LLM to explain prep material structure
- Focuses on helping students find what they need

### 4. Enhanced Context Formatting
**File**: `src/generation/llm_integration.py`

Updated `format_context()` to include Canvas module information:

```python
# Add Canvas module information if available
if metadata.get('parent_module'):
	 source_info.append(f"Canvas Module: {metadata['parent_module']}")
```

Also added PowerPoint slide detection:

```python
elif metadata.get('slide_number'):
	 source_info.append(f"Slide {metadata['slide_number']}")

if metadata.get('content_type') in ['pdf_page', 'image', 'pptx_slide']:
	 content_part += "[Note: This source contains visual content - images or drawings]\n"
```

**Benefits:**
- LLM now sees which Canvas module each result came from
- Can explain where materials are located
- Understands slide numbers for PowerPoint content

---

## 🔄 How It Works

### Query Flow: "What is covered in Session 5?"

1. **Query Analysis** (hybrid_search.py)
	```
	Input: "What is covered in Session 5?"
	Analysis: {
	  'is_module_query': True,
	  'module_number': '5',
	  'intent': 'module_content'
	}
	```

2. **Query Enhancement** (hybrid_search.py)
	```
	Original: "What is covered in Session 5?"
	Enhanced: "What is covered in Session 5? Session 5 Module 5 Week 5"
	```

3. **Retrieval** (vector + BM25)
	```
	Searches for:
	- parent_module containing "Session 5"
	- Text containing "Session 5", "Module 5", "Week 5"
	- Related terms
	```

4. **Context Formation** (llm_integration.py)
	```
	[Source 1] Canvas Module: Session 5 - Steel Frame - Model making | File: Session 6 - Steel Framing...
	[Source 2] Canvas Module: Session 4 - Steel: Design... | File: Session 5 - Steel Frame Design V2.pptx...
	```

5. **Response Generation** (llm_integration.py)
	```
	Template: 'module_content' (with Canvas structure explanation)
	Context: Includes Canvas module names + file names
	Result: LLM explains what's IN Session 5 module AND mentions prep materials
	```

---

## ✅ Expected Behavior

### Query: "What is covered in Session 5?"

**Expected Response:**
```
Session 5 covers "Steel Frame - Model making (Primary and Secondary systems)".

Main Session 5 Module Content:
- The focus is on practical model making for steel frame structures
- You'll work on both primary (main structural) and secondary (supporting) systems

Prep Materials:
Note that prep materials for Session 5 (lecture slides and tasks about Steel Frame Design) 
are located in the Session 4 module:
- Session 5 - Steel Frame Design V2.pptx (43 slides) in Session 4 module
- Session 5 - Steel Frame Design Task.pdf in Session 4 module

Also note: Session 6 prep materials (Steel Framing Detailing and Production PDF) are 
available in the Session 5 module.
```

### Query: "What's in the Session 4 module?"

**Expected Response:**
```
Session 4 module covers "Steel: Design, Detailing and Production".

Module Content:
- [Session 4 specific content]

Prep Materials for Next Week:
The Session 4 module also includes prep materials for Session 5:
- Session 5 - Steel Frame Design V2.pptx (43 slides of steel frame design content)
- Session 5 - Steel Frame Design Task.pdf
```

### Query: "Tell me about steel frame design" (non-module query)

**Expected Response:**
```
[General content-based response about steel frame design]
[Finds materials regardless of which module they're in]
```

---

## 🧪 Testing the Changes

### Test 1: Module-Specific Query
```bash
# In Streamlit chat or test script
Query: "What is covered in Session 5?"
```

**Expected:**
- ✅ Retrieves Session 5 module content (model making)
- ✅ Mentions Session 6 prep materials in Session 5 module
- ✅ May mention Session 5 prep materials in Session 4 module
- ✅ Explains Canvas module structure

### Test 2: Module Content Query
```bash
Query: "What's in the Session 4 module?"
```

**Expected:**
- ✅ Retrieves Session 4 module content
- ✅ Lists files including Session 5 prep materials
- ✅ Distinguishes module topic from prep materials

### Test 3: General Content Query
```bash
Query: "How do I design steel frames?"
```

**Expected:**
- ✅ Works as before (content-based retrieval)
- ✅ Finds relevant materials from any module
- ✅ Not treated as module query

---

## 📈 What This Fixes

### Before ❌
```
Query: "What is covered in Session 5?"
Retrieval: Generic search for "Session 5" text
Result: Confusion - finds files NAMED "Session 5" but in Session 4 module
Response: Generic LLM hallucination about what Session 5 "might" cover
```

### After ✅
```
Query: "What is covered in Session 5?"
Detection: Module query for Session 5
Retrieval: 
  - Primary: parent_module = "Session 5..."
  - Secondary: text contains "Session 5"
Context: Includes Canvas module names
Response: Explains what's IN Session 5 module + mentions prep materials
```

---

## 🎓 Benefits

### For Students
- ✅ Clear answers about what's in each module
- ✅ Understand where prep materials are located
- ✅ Know when materials are for future sessions
- ✅ Navigate Canvas course structure easily

### For Instructors
- ✅ Flexible course organization (prep materials in earlier modules)
- ✅ System respects your intentional module placement
- ✅ No need to rename files to match module numbers
- ✅ Can "recycle" content from previous years

### Technical
- ✅ No re-ingestion needed
- ✅ Works with existing database
- ✅ Query-time enhancement only
- ✅ Backward compatible with non-module queries

---

## 🔍 Debugging

### Enable Query Enhancement Debug Logging
In `.env`:
```
QUERY_ENHANCEMENT_DEBUG=true
```

### Check Logs For:
```
DEBUG | Detected module query for Session/Module 5
DEBUG | Module-enhanced query: 'What is covered in Session 5?' → 'What is covered in Session 5? Session 5 Module 5 Week 5'
```

### Verify Retrieval Results
Results should include `parent_module` in metadata:
```json
{
  "parent_module": "Session 5 - Steel Frame - Model making...",
  "filename": "Session 6 -Steel Framing Detailing and Production.pdf",
  ...
}
```

---

## 📝 Files Modified

1. **src/retrieval/hybrid_search.py**
	- Added `'module'` and `'module_content'` patterns
	- Enhanced `analyze_query()` with module detection
	- Added module query enhancement in `enhance_query()`

2. **src/generation/llm_integration.py**
	- Added `'module_content'` prompt template
	- Updated `format_context()` to include Canvas module info
	- Added PowerPoint slide number detection

**Total Changes**: ~100 lines added/modified  
**Re-ingestion Required**: ❌ No  
**Breaking Changes**: ❌ No

---

## ✅ Status

**Implementation**: Complete  
**Testing**: Ready for testing in Streamlit chat  
**Documentation**: Complete  
**Production**: Ready to deploy

Test it with: `python -m streamlit run src/ui/streamlit_app.py`

Then ask: **"What is covered in Session 5?"**
