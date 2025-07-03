"""
Complete pipeline script for Canvas RAG system.
Runs ingestion, processing, and indexing in sequence.
"""

import asyncio
import sys
from pathlib import Path
import argparse

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion.canvas_ingester import CanvasIngester
from src.processing.content_processor import ContentProcessor
from src.indexing.vector_store import IndexBuilder
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def run_ingestion(course_id: str = None, page_url: str = None):
    """Run Canvas content ingestion."""
    if page_url:
        logger.info(f"Starting single page ingestion for: {page_url}")
        course_id = course_id or settings.canvas_course_id
        if not course_id:
            raise ValueError("Course ID must be provided for single page ingestion")
        
        async with CanvasIngester() as ingester:
            metadata = await ingester.ingest_specific_page(course_id, page_url)
            logger.info(f"Single page ingestion complete: {metadata.get('page', {}).get('title', 'Unknown')}")
            return metadata
    else:
        logger.info("Starting Canvas course content ingestion...")
        course_id = course_id or settings.canvas_course_id
        if not course_id:
            raise ValueError("Course ID must be provided either as argument or in .env file")
        
        async with CanvasIngester() as ingester:
            metadata = await ingester.ingest_course_content(course_id)
            logger.info(f"Course ingestion complete: {len(metadata.get('pages', []))} pages, {len(metadata.get('files', []))} files")
            return metadata

def run_processing():
    """Run content processing."""
    logger.info("Starting content processing...")
    
    # Find metadata files (both course and single page)
    course_metadata_files = list(settings.raw_data_dir.glob("course_*_metadata.json"))
    page_metadata_files = list(settings.raw_data_dir.glob("page_*_metadata.json"))
    
    all_metadata_files = course_metadata_files + page_metadata_files
    
    if not all_metadata_files:
        raise FileNotFoundError("No metadata files found. Run ingestion first.")
    
    processor = ContentProcessor()
    
    for metadata_file in all_metadata_files:
        logger.info(f"Processing {metadata_file}")
        segments = processor.process_course_content(metadata_file)
        logger.info(f"Processed {len(segments)} content segments")
    
    return len(all_metadata_files)

def run_indexing(embedding_model_type: str = "openai"):
    """Run content indexing."""
    logger.info("Starting content indexing...")
    
    # Find processed content files
    processed_files = list(settings.processed_data_dir.glob("processed_*.json"))
    
    if not processed_files:
        raise FileNotFoundError("No processed content files found. Run processing first.")
    
    # Use latest processed file
    latest_file = sorted(processed_files)[-1]
    logger.info(f"Building index from {latest_file}")
    
    index_builder = IndexBuilder(embedding_model_type=embedding_model_type)
    index_builder.build_index(latest_file)
    
    logger.info("Indexing complete")

async def main():
    """Main pipeline execution."""
    parser = argparse.ArgumentParser(description="Canvas RAG Pipeline")
    parser.add_argument("--course-id", help="Canvas course ID")
    parser.add_argument("--page-url", help="Specific Canvas page URL slug for single-page ingestion")
    parser.add_argument("--skip-ingestion", action="store_true", help="Skip ingestion step")
    parser.add_argument("--skip-processing", action="store_true", help="Skip processing step")
    parser.add_argument("--skip-indexing", action="store_true", help="Skip indexing step")
    parser.add_argument("--embedding-model", default="openai", choices=["openai", "nomic"], 
                       help="Embedding model to use")
    
    args = parser.parse_args()
    
    try:
        # Check required environment variables
        if not settings.openai_api_key and args.embedding_model == "openai":
            logger.error("OpenAI API key not found in environment variables")
            return
        
        if not settings.canvas_api_url or not settings.canvas_api_token:
            logger.error("Canvas API credentials not found in environment variables")
            return
        
        logger.info("Starting Canvas RAG pipeline...")
        
        # Step 1: Ingestion
        if not args.skip_ingestion:
            if args.page_url:
                logger.info(f"Running single page ingestion for: {args.page_url}")
            else:
                logger.info("Running full course ingestion")
            await run_ingestion(args.course_id, args.page_url)
        else:
            logger.info("Skipping ingestion step")
        
        # Step 2: Processing
        if not args.skip_processing:
            run_processing()
        else:
            logger.info("Skipping processing step")
        
        # Step 3: Indexing
        if not args.skip_indexing:
            run_indexing(args.embedding_model)
        else:
            logger.info("Skipping indexing step")
        
        logger.info("🎉 Pipeline completed successfully!")
        logger.info("You can now run the chat interface with: streamlit run src/ui/chat_app.py")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
