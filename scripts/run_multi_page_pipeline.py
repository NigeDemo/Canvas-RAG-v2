"""
Multi-page pipeline script for Canvas RAG system.
Runs the complete pipeline (ingestion → processing → indexing) for multiple Canvas content types.

This is a higher-level orchestrator that uses:
- src.ingestion.canvas_ingester for Canvas API interaction
- src.processing.content_processor for content processing
- src.indexing.vector_store for indexing

Supports three Canvas content types:
- Pages: Individual course pages
- Assignments: Assignment descriptions, rubrics, and attached files
- Modules: Course structure with embedded content

Use this script when you need to process multiple Canvas content items in one batch.
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion.canvas_ingester import CanvasIngester
from src.processing.content_processor import ContentProcessor
from src.indexing.vector_store import IndexBuilder
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def ingest_multiple_pages(course_id: str, page_urls: list[str]):
    """
    Ingest multiple Canvas pages.
    
    Args:
        course_id: Canvas course ID
        page_urls: List of page URL slugs to ingest
    """
    logger.info(f"Starting multi-page ingestion for {len(page_urls)} pages")
    
    async with CanvasIngester() as ingester:
        for page_url in page_urls:
            try:
                logger.info(f"Ingesting page: {page_url}")
                metadata = await ingester.ingest_specific_page(course_id, page_url)
                page_title = metadata.get('page', {}).get('title', 'Unknown')
                logger.info(f"✅ Completed: {page_title}")
            except Exception as e:
                logger.error(f"❌ Failed to ingest {page_url}: {e}")
                # Continue with next page
                continue
    
    logger.info("Multi-page ingestion complete")

async def ingest_assignments(course_id: str, assignment_ids: list[int]):
    """
    Ingest multiple Canvas assignments.
    
    Args:
        course_id: Canvas course ID
        assignment_ids: List of assignment IDs to ingest
    """
    if not assignment_ids:
        logger.info("No assignments to ingest")
        return
    
    logger.info(f"Starting assignment ingestion for {len(assignment_ids)} assignments")
    
    async with CanvasIngester() as ingester:
        for assignment_id in assignment_ids:
            try:
                logger.info(f"Ingesting assignment ID: {assignment_id}")
                metadata = await ingester.ingest_assignment(course_id, assignment_id)
                assignment_name = metadata.get('assignment', {}).get('name', 'Unknown')
                logger.info(f"✅ Completed: {assignment_name}")
            except Exception as e:
                logger.error(f"❌ Failed to ingest assignment {assignment_id}: {e}")
                # Continue with next assignment
                continue
    
    logger.info("Assignment ingestion complete")

async def ingest_modules(course_id: str):
    """
    Ingest all Canvas modules for a course.
    
    Args:
        course_id: Canvas course ID
    """
    logger.info(f"Starting module ingestion for course {course_id}")
    
    async with CanvasIngester() as ingester:
        try:
            metadata = await ingester.ingest_modules(course_id)
            num_modules = len(metadata.get('modules', []))
            logger.info(f"✅ Completed: {num_modules} modules ingested")
        except Exception as e:
            logger.error(f"❌ Failed to ingest modules: {e}")
            raise
    
    logger.info("Module ingestion complete")


def process_all_pages():
    """Process all ingested content (pages, assignments, modules) and consolidate into single file."""
    logger.info("Processing all ingested content...")
    
    processor = ContentProcessor()
    
    # Find all metadata files
    page_metadata_files = list(settings.raw_data_dir.glob("page_*_metadata.json"))
    assignment_metadata_files = list(settings.raw_data_dir.glob("assignment_*_metadata.json"))
    module_metadata_files = list(settings.raw_data_dir.glob("modules_*_metadata.json"))
    
    all_metadata_files = page_metadata_files + assignment_metadata_files + module_metadata_files
    
    if not all_metadata_files:
        raise FileNotFoundError("No metadata files found. Run ingestion first.")
    
    logger.info(f"Found metadata files:")
    logger.info(f"  - Pages: {len(page_metadata_files)}")
    logger.info(f"  - Assignments: {len(assignment_metadata_files)}")
    logger.info(f"  - Modules: {len(module_metadata_files)}")
    logger.info(f"  - Total: {len(all_metadata_files)}")
    
    all_segments = []
    
    for metadata_file in all_metadata_files:
        logger.info(f"Processing {metadata_file.name}")
        segments = processor.process_course_content(metadata_file)
        all_segments.extend(segments)
        logger.info(f"  → {len(segments)} segments")
    
    # Save consolidated processed content
    consolidated_path = settings.processed_data_dir / "processed_multi_page_consolidated.json"
    with open(consolidated_path, 'w', encoding='utf-8') as f:
        json.dump(all_segments, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Total segments processed: {len(all_segments)}")
    logger.info(f"Saved consolidated content to: {consolidated_path.name}")
    
    return all_segments, len(all_metadata_files)

def index_all_content(embedding_model_type: str = "openai"):
    """Index all processed content at once."""
    logger.info("Indexing all content...")
    
    # Use the consolidated file
    consolidated_file = settings.processed_data_dir / "processed_multi_page_consolidated.json"
    
    if not consolidated_file.exists():
        raise FileNotFoundError(f"Consolidated file not found: {consolidated_file}")
    
    logger.info(f"Using consolidated file: {consolidated_file.name}")
    
    # Build index (includes both vector and BM25)
    index_builder = IndexBuilder(embedding_model_type=embedding_model_type)
    index_builder.build_index(consolidated_file)
    
    logger.info("✅ Indexing complete")

async def main():
    """Main execution."""
    # Load configuration from settings
    course_id = settings.canvas_course_id
    page_urls = settings.multi_page_urls_list
    assignment_ids = settings.assignment_ids_list
    ingest_modules_flag = settings.should_ingest_modules
    
    # Validate configuration
    if not course_id:
        logger.error("CANVAS_COURSE_ID not set in .env file")
        raise ValueError("CANVAS_COURSE_ID is required. Please set it in your .env file.")
    
    if not page_urls and not assignment_ids and not ingest_modules_flag:
        logger.error("No content specified for ingestion")
        raise ValueError("At least one of CANVAS_MULTI_PAGE_URLS, CANVAS_ASSIGNMENT_IDS, or CANVAS_INGEST_MODULES must be set.")
    
    logger.info("="*70)
    logger.info("MULTI-CONTENT CANVAS RAG PIPELINE")
    logger.info("="*70)
    logger.info(f"Course ID: {course_id}")
    if page_urls:
        logger.info(f"Pages to process: {', '.join(page_urls)}")
    if assignment_ids:
        logger.info(f"Assignments to process: {', '.join(map(str, assignment_ids))}")
    if ingest_modules_flag:
        logger.info(f"Modules: Will ingest all course modules")
    logger.info("="*70)
    
    try:
        # Step 1: Ingest all content
        logger.info("\n📥 STEP 1: Ingesting content...")
        
        if page_urls:
            logger.info("  → Ingesting pages...")
            await ingest_multiple_pages(course_id, page_urls)
        
        if assignment_ids:
            logger.info("  → Ingesting assignments...")
            await ingest_assignments(course_id, assignment_ids)
        
        if ingest_modules_flag:
            logger.info("  → Ingesting modules...")
            await ingest_modules(course_id)
        
        # Step 2: Process all content into single dataset
        logger.info("\n⚙️  STEP 2: Processing content...")
        all_segments, num_files = process_all_pages()
        
        # Step 3: Index everything at once
        logger.info("\n🔍 STEP 3: Building indices (Vector + BM25)...")
        index_all_content()
        
        logger.info("\n" + "="*70)
        logger.info("✅ MULTI-CONTENT PIPELINE COMPLETE!")
        logger.info("="*70)
        logger.info(f"Content items processed: {num_files}")
        logger.info(f"Total segments: {len(all_segments)}")
        logger.info("Vector store and BM25 index ready for queries")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
