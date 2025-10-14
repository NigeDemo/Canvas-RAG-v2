# Canvas Content Types - Understanding & Configuration

## What You Discovered 🔍

After listing your Canvas course content, here's what we found:

### ✅ Available as Pages (Can Process):
- **Home Page**: `home-page` (marked as FRONT PAGE)
- **Construction Drawing Package**: `construction-drawing-package-2`
- **Plus 57 other pages!**

### ❌ Not Available as Pages (Need Different Approach):
- **Syllabus**: Actually an Assignment (#304961 - "Portfolio")
- **Modules**: Organizational containers, not content pages

---

## Recommended Configuration

### Option 1: Key Architecture Content Pages

Based on the course listing, here are the most relevant pages for architecture education:

```bash
CANVAS_MULTI_PAGE_URLS=home-page,construction-drawing-package-2,concrete-frame-precedent-studies,advance-concrete-formation,advance-steel-fabrication,advances-double-layered-timber-folding,mass-timber-in-architecture,example-structures-and-building-skins
```

**Content Focus**: Structural systems, materials, precedent studies

### Option 2: Student Resources + Construction Content

```bash
CANVAS_MULTI_PAGE_URLS=home-page,your-student-journey,construction-drawing-package-2,concrete-frame-precedent-studies,advance-concrete-formation,advance-steel-fabrication
```

**Content Focus**: Mix of student support and technical content

### Option 3: Minimal Test Set

```bash
CANVAS_MULTI_PAGE_URLS=home-page,construction-drawing-package-2
```

**Content Focus**: Just the essentials for testing

---

## Why Your Original Config Failed

### ❌ What You Had:
```bash
CANVAS_MULTI_PAGE_URLS=home,syllabus,modules,construction-drawing-package-2
```

### 🔍 What Went Wrong:

| Your Input | What Happened | Actual URL |
|-----------|---------------|------------|
| `home` | ❌ Not Found | Should be `home-page` |
| `syllabus` | ❌ Not Found | It's an Assignment, not a Page |
| `modules` | ❌ Not Found | Organizational structure, not a Page |
| `construction-drawing-package-2` | ✅ Success! | Correct |

---

## Canvas Content Type Hierarchy

```
Canvas Course
│
├── Pages (✅ Can process with current system)
│   ├── home-page [FRONT PAGE]
│   ├── construction-drawing-package-2
│   ├── concrete-frame-precedent-studies
│   └── ... (56 more pages)
│
├── Assignments (⚠️ Requires different API endpoint)
│   ├── Portfolio (ID: 304961)
│   └── Portfolio – Second Opportunity (ID: 304319)
│
├── Modules (📚 Organizational containers)
│   ├── Student Resources
│   │   └── Contains: Pages, Files, External Links
│   ├── Session 1 - Structural Behaviour
│   │   └── Contains: PDF files, Pages, External URLs
│   └── ... (13 more modules)
│
└── Files (📄 PDFs, images, etc.)
    ├── Session 1 - Structural Behaviour.pdf
    ├── Session 2 - Concrete.pdf
    └── ... (many more files)
```

---

## What Can You Process Right Now?

### ✅ Ready to Process (Current System):
- **Pages**: All 59 pages including home-page
- **Files**: PDFs and images (if referenced in pages)

### ⚠️ Needs Enhancement (Future):
- **Assignments**: Requires assignment-specific API calls
- **Module Structure**: Could create a "table of contents" view
- **Direct File Processing**: Currently only processes files referenced in pages

---

## Recommended Next Steps

### Step 1: Update .env with Correct Page URLs

Choose one of the options above, or create your own selection:

```bash
# Minimal test (recommended to start)
CANVAS_MULTI_PAGE_URLS=home-page,construction-drawing-package-2

# Or more comprehensive
CANVAS_MULTI_PAGE_URLS=home-page,construction-drawing-package-2,concrete-frame-precedent-studies,advance-concrete-formation,advance-steel-fabrication,advances-double-layered-timber-folding
```

### Step 2: Clear Database

```powershell
python scripts/clear_database.py
```

### Step 3: Run Multi-Page Pipeline

```powershell
python scripts/run_multi_page_pipeline.py
```

---

## Pro Tips 💡

### Finding More Pages to Add:

Run the listing script again to see all available pages:
```powershell
python scripts/list_canvas_content.py
```

Then pick the URLs you want from the "📄 PAGES" section.

### Page URL Format:
- URLs use lowercase and hyphens
- Spaces become hyphens: "Concrete Frame" → `concrete-frame`
- Special characters removed: "Week 1 Glossary" → `week-1-glossary`

### Common Pitfalls:
- ❌ Don't use: `home`, `syllabus`, `modules` (generic names)
- ✅ Use exact URLs from the listing: `home-page`, `construction-drawing-package-2`

---

## Future Enhancements (Phase 4?)

If you need to process assignments or modules, we could add:

1. **Assignment Processing**:
   ```python
   # Process assignment content (description, rubrics, etc.)
   course.get_assignment(304961)
   ```

2. **Module Structure Extraction**:
   ```python
   # Create a map of course structure
   modules = course.get_modules()
   ```

3. **Direct PDF Processing**:
   ```python
   # Process all PDFs even if not linked in pages
   files = course.get_files()
   ```

---

## Quick Reference

**List all available content:**
```powershell
python scripts/list_canvas_content.py
```

**Check your current config:**
```powershell
python -c "from src.config.settings import settings; print('Pages:', settings.multi_page_urls_list)"
```

**Clear and rebuild:**
```powershell
python scripts/clear_database.py
python scripts/run_multi_page_pipeline.py
```

---

**Now you know what's available!** Update your `.env` with correct page URLs and try again. 🚀
