#!/usr/bin/env python3
"""
Demonstration script for single Canvas page ingestion.
Shows how to fetch and process content from a specific Canvas page.
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.canvas_ingester import CanvasIngester
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def demo_single_page_ingestion():
    """Demonstrate single page ingestion functionality."""
    
    print("🎯 Canvas RAG v2 - Single Page Ingestion Demo")
    print("=" * 60)
    
    # Configuration
    course_id = os.getenv("CANVAS_COURSE_ID") or "45166"
    page_url = "construction-drawing-package-2"
    
    print(f"📚 Course ID: {course_id}")
    print(f"📄 Page URL: {page_url}")
    print(f"🔗 Canvas API URL: {settings.canvas_api_url}")
    
    # Check required environment variables
    if not settings.canvas_api_token:
        print("❌ CANVAS_API_TOKEN not found in environment variables")
        print("Please set your Canvas API token in the .env file")
        return
    
    try:
        # Initialize ingester
        print(f"\n🔄 Initializing Canvas ingester...")
        async with CanvasIngester() as ingester:
            print("✅ Connected to Canvas API")
            
            # Ingest the specific page
            print(f"\n📥 Ingesting page: {page_url}")
            metadata = await ingester.ingest_specific_page(course_id, page_url)
            
            if not metadata:
                print("❌ Failed to ingest page. Check course ID and page URL.")
                return
            
            # Display results
            page_info = metadata.get("page", {})
            files = metadata.get("files", [])
            
            print("✅ Page ingestion successful!")
            print(f"\n📊 Ingestion Results:")
            print(f"- Page Title: {page_info.get('title', 'Unknown')}")
            print(f"- Content Length: {len(page_info.get('body', ''))} characters")
            print(f"- Referenced Files: {len(files)}")
            print(f"- Last Updated: {page_info.get('updated_at', 'Unknown')}")
            
            # Show referenced files
            if files:
                print(f"\n📎 Referenced Files:")
                for file_info in files:
                    print(f"  • {file_info['filename']}")
                    print(f"    Type: {file_info.get('content_type', 'unknown')}")
                    print(f"    Size: {file_info.get('size', 0):,} bytes")
                    print(f"    Path: {file_info.get('path', 'N/A')}")
                    print()
            
            # Show content preview
            body = page_info.get('body', '')
            if body:
                # Extract first few sentences for preview
                import re
                text_only = re.sub(r'<[^>]+>', '', body)
                sentences = text_only.split('.')[:3]
                preview = '. '.join(sentences) + '...' if len(sentences) >= 3 else text_only
                
                print(f"\n📝 Content Preview:")
                print(f"'{preview[:200]}{'...' if len(preview) > 200 else ''}'")
            
            # Show metadata file location
            safe_page_name = page_url.replace("-", "_")
            metadata_path = settings.raw_data_dir / f"page_{safe_page_name}_metadata.json"
            print(f"\n💾 Metadata saved to:")
            print(f"   {metadata_path}")
            
            # Next steps
            print(f"\n🚀 Next Steps:")
            print(f"1. Process the content:")
            print(f"   python scripts/run_pipeline.py --skip-ingestion --course-id {course_id}")
            print(f"2. Start the chat interface:")
            print(f"   streamlit run src/ui/chat_app.py")
            print(f"3. Query the ingested page content!")
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Error: {e}")
        print(f"\nTroubleshooting:")
        print(f"- Check your Canvas API token and URL")
        print(f"- Verify the course ID: {course_id}")
        print(f"- Confirm the page URL slug: {page_url}")
        print(f"- Make sure you have access to the Canvas course")

def main():
    """Main function with user interaction."""
    
    # Allow user to specify course and page
    if len(sys.argv) > 1:
        course_id = sys.argv[1]
        os.environ["CANVAS_COURSE_ID"] = course_id
        print(f"Using course ID from command line: {course_id}")
    
    if len(sys.argv) > 2:
        page_url = sys.argv[2]
        print(f"Using page URL from command line: {page_url}")
        # Would need to modify the demo function to accept this parameter
    
    # Run the demo
    asyncio.run(demo_single_page_ingestion())

if __name__ == "__main__":
    print(__doc__)
    main()
