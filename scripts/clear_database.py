"""
Clear and backup the ChromaDB database before running multi-page pipeline.
This prevents duplicate entries when re-processing pages.
"""

import sys
from pathlib import Path
import shutil
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

def backup_database():
    """Create a timestamped backup of the current database."""
    db_path = Path(settings.chroma_persist_directory)
    
    if not db_path.exists():
        logger.info("No existing database to backup")
        return None
    
    # Create backup directory
    backup_dir = db_path.parent / "chroma_db_backups"
    backup_dir.mkdir(exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"chroma_db_backup_{timestamp}"
    
    logger.info(f"Creating backup: {backup_path}")
    shutil.copytree(db_path, backup_path)
    logger.info(f"✅ Backup created successfully")
    
    return backup_path

def clear_database():
    """Clear the ChromaDB database."""
    db_path = Path(settings.chroma_persist_directory)
    
    if not db_path.exists():
        logger.info("No existing database to clear")
        return
    
    logger.info(f"Clearing database: {db_path}")
    shutil.rmtree(db_path)
    logger.info("✅ Database cleared successfully")

def clear_processed_data():
    """Clear processed data files."""
    processed_dir = Path(settings.processed_data_dir)
    
    if not processed_dir.exists():
        logger.info("No processed data to clear")
        return
    
    processed_files = list(processed_dir.glob("processed_*.json"))
    
    if not processed_files:
        logger.info("No processed files to clear")
        return
    
    logger.info(f"Found {len(processed_files)} processed files")
    
    for file in processed_files:
        file.unlink()
        logger.info(f"  Deleted: {file.name}")
    
    logger.info("✅ Processed data cleared")

def main():
    """Main execution."""
    print("="*70)
    print("DATABASE CLEANUP UTILITY")
    print("="*70)
    print()
    print("This will:")
    print("  1. Create a timestamped backup of your current database")
    print("  2. Clear the ChromaDB vector database")
    print("  3. Clear processed content files")
    print()
    print("Your raw ingested data will NOT be affected.")
    print("="*70)
    print()
    
    # Ask for confirmation
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Cancelled. Database unchanged.")
        return
    
    print()
    logger.info("Starting database cleanup...")
    
    try:
        # Step 1: Backup
        print("\n📦 Step 1: Creating backup...")
        backup_path = backup_database()
        if backup_path:
            print(f"✅ Backup saved to: {backup_path}")
        
        # Step 2: Clear database
        print("\n🗑️  Step 2: Clearing database...")
        clear_database()
        
        # Step 3: Clear processed data
        print("\n🗑️  Step 3: Clearing processed data...")
        clear_processed_data()
        
        print("\n" + "="*70)
        print("✅ CLEANUP COMPLETE!")
        print("="*70)
        print("\nYou can now run the multi-page pipeline:")
        print("  python scripts/run_multi_page_pipeline.py")
        print()
        
        if backup_path:
            print("💡 To restore your backup if needed:")
            print(f"  Remove-Item '{settings.chroma_persist_directory}' -Recurse")
            print(f"  Copy-Item '{backup_path}' '{settings.chroma_persist_directory}' -Recurse")
        
        print("="*70)
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        print(f"\n❌ Error: {e}")
        if backup_path:
            print(f"\n💡 Your backup is safe at: {backup_path}")
        raise

if __name__ == "__main__":
    main()
