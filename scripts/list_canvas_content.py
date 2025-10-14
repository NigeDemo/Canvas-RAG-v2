"""
List all available content in a Canvas course to help identify correct URLs.
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.config.settings import settings
from canvasapi import Canvas
from src.utils.logger import get_logger

logger = get_logger(__name__)

def list_course_content():
    """List all pages, assignments, and modules in a Canvas course."""
    
    canvas = Canvas(settings.canvas_api_url, settings.canvas_api_token)
    course = canvas.get_course(settings.canvas_course_id)
    
    print("="*70)
    print(f"CANVAS COURSE CONTENT: {course.name}")
    print("="*70)
    
    # List Pages
    print("\n📄 PAGES:")
    print("-"*70)
    try:
        pages = list(course.get_pages())
        if pages:
            for i, page in enumerate(pages, 1):
                url_slug = page.url if hasattr(page, 'url') else 'unknown'
                front_page = " [FRONT PAGE]" if hasattr(page, 'front_page') and page.front_page else ""
                print(f"{i}. {page.title}{front_page}")
                print(f"   URL: {url_slug}")
                print()
        else:
            print("  No pages found")
    except Exception as e:
        print(f"  Error listing pages: {e}")
    
    # List Assignments
    print("\n📝 ASSIGNMENTS:")
    print("-"*70)
    try:
        assignments = list(course.get_assignments())
        if assignments:
            for i, assignment in enumerate(assignments, 1):
                print(f"{i}. {assignment.name}")
                if hasattr(assignment, 'html_url'):
                    # Extract slug from URL
                    url_parts = assignment.html_url.split('/')
                    if 'assignments' in url_parts:
                        idx = url_parts.index('assignments')
                        if idx + 1 < len(url_parts):
                            print(f"   ID: {url_parts[idx + 1]}")
                print()
        else:
            print("  No assignments found")
    except Exception as e:
        print(f"  Error listing assignments: {e}")
    
    # List Modules
    print("\n📚 MODULES:")
    print("-"*70)
    try:
        modules = list(course.get_modules())
        if modules:
            for i, module in enumerate(modules, 1):
                print(f"{i}. {module.name}")
                
                # List module items
                try:
                    items = list(module.get_module_items())
                    if items:
                        for j, item in enumerate(items, 1):
                            item_type = item.type if hasattr(item, 'type') else 'unknown'
                            item_title = item.title if hasattr(item, 'title') else 'untitled'
                            print(f"   {i}.{j} [{item_type}] {item_title}")
                except:
                    pass
                print()
        else:
            print("  No modules found")
    except Exception as e:
        print(f"  Error listing modules: {e}")
    
    print("="*70)
    print("\n💡 USAGE:")
    print("  - For PAGES: Use the 'URL' slug in CANVAS_MULTI_PAGE_URLS")
    print("  - For FRONT PAGE: Will be handled specially (coming soon)")
    print("  - For ASSIGNMENTS: Note the ID number")
    print("  - For MODULES: Module content requires special handling")
    print("="*70)

if __name__ == "__main__":
    list_course_content()
