# Documentation Index

Last updated: 2025-10-14

This index points to the authoritative, up-to-date documentation for Canvas RAG v2 and clearly separates historical notes kept for context.

## Authoritative docs (start here)

* Overview and architecture: `../README.md`
* Quick start: `../QUICKSTART.md`
* Configuration: `docs/CONFIGURATION.md`
* API and modules map: `docs/API.md`
* Repository structure: `../REPOSITORY_STRUCTURE.md`
* Streamlit apps comparison (UI): `../STREAMLIT_APPS_COMPARISON.md`
* Vision AI setup: `../VISION_AI_SETUP.md`
* Vision AI guide (usage, tips): `../VISION_AI_GUIDE.md`
* Section-aware processing (in code): `src/processing/content_processor.py`
  * Verification helper: `check_section_headings.py`
* Retrieval and query enhancement: `src/retrieval/hybrid_search.py`
  * Hybrid index plumbing: `src/indexing/vector_store.py`
* Embeddings and models: `src/embeddings/multimodal_embeddings.py`
* Technical notes (deeper engineering details): `../TECHNICAL.md`
* PyMuPDF migration rationale: `../PYMUPDF_MIGRATION.md`
* Comprehensive testing plan (regressions): `../COMPREHENSIVE_TESTING_PLAN.md`

## Active session planning

* Session start (current): `../START_HERE_NEXT_SESSION.md`
* Next session priorities and Phase 3 focus: `../NEXT_SESSION_TASKS.md`

## Ingestion references

* Canvas content types: `docs/CANVAS_CONTENT_TYPES.md`
* Multi-page ingestion: `docs/MULTI_PAGE_INGESTION.md`

## Testing and diagnostics

* Unit/integration tests: `tests/`
* Vision diagnostic: `test_vision_rag_session5.py`
* Database inspection: `check_database.py`
* Section detection checker: `check_section_headings.py`

## Historical context (archived)

These documents are kept for history and provenance but are not authoritative. Prefer the files listed in “Authoritative docs” above.

Archived docs are now under `docs/archive/`:

* `docs/archive/SESSION_SUMMARY_VISION_FIX.md` — Session summary of the module-query fix
* `docs/archive/VISION_CHAT_MODULE_FIX_COMPLETE.md` — Technical details of that fix
* `docs/archive/MODULE_QUERY_ENHANCEMENT_COMPLETE.md` — Older milestone summary
* `docs/archive/CRITICAL_ISSUE_IMAGE_RETRIEVAL.md` — Prior incident write-up
* `docs/archive/END_OF_DAY_SUMMARY.md` — Daily notes
* `docs/archive/READY_FOR_TESTING.md` — Older release gating notes
* `docs/archive/REPO_CLEANUP_OCT3.md` — Cleanup worklog
* `docs/archive/PROJECT_STATUS.md` — Status snapshot superseded by README + START_HERE
* `docs/archive/NEW_AGENT_START_HERE.md` — Onboarding notes for older session

If an archived document still contains unique, living guidance, consider merging its relevant content into the authoritative docs and leaving a short redirect note in the archived file.
