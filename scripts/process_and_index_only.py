"""
Quick pipeline script to process and index existing raw data.
Use this when you already have raw metadata files and just need to re-process/re-index.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.processing.content_processor import ContentProcessor
from src.indexing.vector_store import IndexBuilder
from src.config.settings import settings
from src.utils.logger import get_logger
import json

logger = get_logger(__name__)

def process_all_content():
    """Process all ingested content (pages, assignments, modules) and consolidate."""
    logger.info("Processing all ingested content...")
    
    processor = ContentProcessor()
    
    # Find all metadata files
    page_metadata_files = list(settings.raw_data_dir.glob("page_*_metadata.json"))
    assignment_metadata_files = list(settings.raw_data_dir.glob("assignment_*_metadata.json"))
    module_metadata_files = list(settings.raw_data_dir.glob("modules_*_metadata.json"))
    
    all_metadata_files = page_metadata_files + assignment_metadata_files + module_metadata_files
    
    if not all_metadata_files:
        raise FileNotFoundError("No metadata files found in data/raw/. Run full pipeline first.")
    
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
    """Index all processed content."""
    logger.info("Indexing all content...")
    
    consolidated_file = settings.processed_data_dir / "processed_multi_page_consolidated.json"
    
    if not consolidated_file.exists():
        raise FileNotFoundError(f"Consolidated file not found: {consolidated_file}")
    
    logger.info(f"Using consolidated file: {consolidated_file.name}")
    
    # Build index (includes both vector and BM25)
    index_builder = IndexBuilder(embedding_model_type=embedding_model_type)
    index_builder.build_index(consolidated_file)
    
    logger.info("✅ Indexing complete")

def main():
    """Main execution - process and index only (no ingestion)."""
    logger.info("="*70)
    logger.info("QUICK PROCESS & INDEX PIPELINE")
    logger.info("(Uses existing raw data - no re-ingestion)")
    logger.info("="*70)
    
    try:
        # Step 1: Process all content
        logger.info("\n⚙️  STEP 1: Processing content...")
        all_segments, num_files = process_all_content()
        
        # Step 2: Index everything
        logger.info("\n🔍 STEP 2: Building indices (Vector + BM25)...")
        index_all_content()
        
        logger.info("\n" + "="*70)
        logger.info("✅ PROCESSING & INDEXING COMPLETE!")
        logger.info("="*70)
        logger.info(f"Content items processed: {num_files}")
        logger.info(f"Total segments: {len(all_segments)}")
        logger.info("Vector store and BM25 index ready for queries")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
