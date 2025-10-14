"""Canvas LMS content ingestion module."""

import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.page import Page
from canvasapi.file import File

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

class CanvasIngester:
    """Handles ingestion of content from Canvas LMS."""
    
    def __init__(self, api_url: str = None, api_token: str = None):
        """
        Initialize Canvas ingester.
        
        Args:
            api_url: Canvas API URL
            api_token: Canvas API token
        """
        self.api_url = api_url or settings.canvas_api_url
        self.api_token = api_token or settings.canvas_api_token
        
        if not self.api_url or not self.api_token:
            raise ValueError("Canvas API URL and token must be provided")
            
        self.canvas = Canvas(self.api_url, self.api_token)
        self.session = None
    
    def get_content_type(self, file: File) -> str:
        """
        Get content type from a Canvas file object.
        
        Args:
            file: Canvas file object
            
        Returns:
            Content type string
        """
        # Try different attribute names for content type
        content_type = getattr(file, 'content_type', None)
        if content_type is None:
            content_type = getattr(file, 'content-type', '')
        if content_type is None:
            content_type = ''
        return content_type
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def get_course(self, course_id: str) -> Course:
        """Get Canvas course by ID."""
        try:
            course = self.canvas.get_course(course_id)
            logger.info(f"Successfully connected to course: {course.name}")
            return course
        except Exception as e:
            logger.error(f"Failed to get course {course_id}: {e}")
            raise
    
    def get_pages(self, course: Course) -> List[Page]:
        """Get all pages from a Canvas course."""
        try:
            pages = list(course.get_pages())
            logger.info(f"Found {len(pages)} pages in course")
            return pages
        except Exception as e:
            logger.error(f"Failed to get pages: {e}")
            return []
    
    def get_files(self, course: Course) -> List[File]:
        """Get all files from a Canvas course."""
        try:
            files = list(course.get_files())
            logger.info(f"Found {len(files)} files in course")
            return files
        except Exception as e:
            logger.error(f"Failed to get files: {e}")
            return []
    
    async def download_file(self, file: File, download_dir: Path) -> Optional[Path]:
        """
        Download a file from Canvas.
        
        Args:
            file: Canvas file object
            download_dir: Directory to save file
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            download_dir.mkdir(parents=True, exist_ok=True)
            file_path = download_dir / file.filename
            
            if file_path.exists():
                logger.info(f"File already exists: {file_path}")
                return file_path
            
            # Download file
            if self.session:
                async with self.session.get(file.url) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        logger.info(f"Downloaded: {file_path}")
                        return file_path
                    else:
                        logger.error(f"Failed to download {file.filename}: HTTP {response.status}")
                        return None
            else:
                # Fallback to synchronous download
                file.download(str(file_path))
                logger.info(f"Downloaded: {file_path}")
                return file_path
                
        except Exception as e:
            logger.error(f"Error downloading {file.filename}: {e}")
            return None
    
    def extract_page_content(self, page: Page) -> Dict[str, Any]:
        """
        Extract content from a Canvas page.
        
        Args:
            page: Canvas page object
            
        Returns:
            Dictionary with page content and metadata
        """
        try:
            # Try to get the body content, handling different attribute names
            body = getattr(page, 'body', None)
            if body is None:
                # Try alternative attribute names
                body = getattr(page, 'content', None)
            if body is None:
                # If still no body, try to get it from the page's show method
                try:
                    full_page = page.show()
                    body = getattr(full_page, 'body', '')
                except:
                    body = ''
            
            content = {
                "id": getattr(page, 'page_id', getattr(page, 'id', 'unknown')),
                "title": getattr(page, 'title', 'Untitled'),
                "url": getattr(page, 'html_url', ''),
                "body": body or "",
                "created_at": str(page.created_at) if hasattr(page, 'created_at') and page.created_at else None,
                "updated_at": str(page.updated_at) if hasattr(page, 'updated_at') and page.updated_at else None,
                "published": getattr(page, 'published', True),
                "type": "page"
            }
            
            logger.debug(f"Extracted content from page: {content['title']}")
            return content
            
        except Exception as e:
            logger.error(f"Error extracting page content {getattr(page, 'title', 'Unknown')}: {e}")
            return {}
    
    async def ingest_course_content(self, course_id: str) -> Dict[str, List[Any]]:
        """
        Ingest all content from a Canvas course.
        
        Args:
            course_id: Canvas course ID
            
        Returns:
            Dictionary with pages and files data
        """
        logger.info(f"Starting ingestion for course {course_id}")
        
        course = self.get_course(course_id)
        
        # Get pages
        pages = self.get_pages(course)
        page_contents = []
        
        for page in pages:
            content = self.extract_page_content(page)
            if content:
                page_contents.append(content)
        
        # Get files
        files = self.get_files(course)
        file_paths = []
        
        download_dir = settings.raw_data_dir / "files"
        
        for file in files:
            # Only download PDFs and images for now
            content_type = self.get_content_type(file)
            
            if content_type in ['application/pdf'] or content_type.startswith('image/'):
                file_path = await self.download_file(file, download_dir)
                if file_path:
                    file_info = {
                        "id": file.id,
                        "filename": file.filename,
                        "path": str(file_path),
                        "url": file.url,
                        "content_type": content_type,
                        "size": getattr(file, 'size', 0),
                        "created_at": str(file.created_at) if hasattr(file, 'created_at') and file.created_at else None,
                        "updated_at": str(file.updated_at) if hasattr(file, 'updated_at') and file.updated_at else None,
                        "type": "file"
                    }
                    file_paths.append(file_info)
        
        # Save metadata
        metadata = {
            "course_id": course_id,
            "course_name": course.name,
            "pages": page_contents,
            "files": file_paths,
            "ingestion_timestamp": str(asyncio.get_event_loop().time())
        }
        
        metadata_path = settings.raw_data_dir / f"course_{course_id}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Ingestion complete. Pages: {len(page_contents)}, Files: {len(file_paths)}")
        return metadata

    def get_specific_page(self, course_id: str, page_url: str) -> Optional[Page]:
        """
        Get a specific Canvas page by URL slug.
        
        Args:
            course_id: Canvas course ID
            page_url: Page URL slug (e.g., "construction-drawing-package-2")
            
        Returns:
            Canvas page object or None if not found
        """
        try:
            course = self.get_course(course_id)
            page = course.get_page(page_url)
            logger.info(f"Successfully retrieved page: {page.title}")
            return page
        except Exception as e:
            logger.error(f"Failed to get page {page_url}: {e}")
            return None
    
    def get_page_files(self, course: Course, page_content: str) -> List[File]:
        """
        Extract and download files referenced in a Canvas page.
        
        Args:
            course: Canvas course object
            page_content: HTML content of the page
            
        Returns:
            List of Canvas file objects found in the page
        """
        try:
            from bs4 import BeautifulSoup
            import re
            
            soup = BeautifulSoup(page_content, 'html.parser')
            file_urls = []
            
            # Find all links to Canvas files
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Match Canvas file URLs
                if '/files/' in href or '/courses/' in href and '/files/' in href:
                    file_urls.append(href)
            
            # Find file IDs from URLs
            file_ids = []
            for url in file_urls:
                # Extract file ID from Canvas URLs
                match = re.search(r'/files/(\d+)', url)
                if match:
                    file_ids.append(match.group(1))
            
            # Get file objects
            files = []
            for file_id in file_ids:
                try:
                    file_obj = course.get_file(file_id)
                    files.append(file_obj)
                    logger.debug(f"Found referenced file: {file_obj.filename}")
                except Exception as e:
                    logger.warning(f"Could not retrieve file {file_id}: {e}")
            
            logger.info(f"Found {len(files)} files referenced in page")
            return files
            
        except Exception as e:
            logger.error(f"Error extracting page files: {e}")
            return []

    async def ingest_specific_page(self, course_id: str, page_url: str) -> Dict[str, Any]:
        """
        Ingest content from a specific Canvas page and its related files.
        
        Args:
            course_id: Canvas course ID  
            page_url: Page URL slug (e.g., "construction-drawing-package-2")
            
        Returns:
            Dictionary with page and files data
        """
        logger.info(f"Starting ingestion for page: {page_url} in course {course_id}")
        
        # Get the specific page
        page = self.get_specific_page(course_id, page_url)
        if not page:
            logger.error(f"Could not retrieve page: {page_url}")
            return {}
        
        # Extract page content
        page_content = self.extract_page_content(page)
        if not page_content:
            logger.error(f"Could not extract content from page: {page_url}")
            return {}
        
        # Get course for file access
        course = self.get_course(course_id)
        
        # Find files referenced in the page
        referenced_files = self.get_page_files(course, page_content.get("body", ""))
        
        # Download referenced files
        download_dir = settings.raw_data_dir / "files"
        file_paths = []
        
        for file in referenced_files:
            # Download PDFs and images
            content_type = self.get_content_type(file)
            
            if (content_type in ['application/pdf'] or 
                content_type.startswith('image/')):
                
                file_path = await self.download_file(file, download_dir)
                if file_path:
                    file_info = {
                        "id": file.id,
                        "filename": file.filename,
                        "path": str(file_path),
                        "url": file.url,
                        "content_type": content_type,
                        "size": getattr(file, 'size', 0),
                        "created_at": str(file.created_at) if hasattr(file, 'created_at') and file.created_at else None,
                        "updated_at": str(file.updated_at) if hasattr(file, 'updated_at') and file.updated_at else None,
                        "type": "file"
                    }
                    file_paths.append(file_info)
        
        # Create metadata for the specific page
        metadata = {
            "course_id": course_id,
            "course_name": course.name,
            "page_url": page_url,
            "page": page_content,
            "files": file_paths,
            "ingestion_timestamp": str(asyncio.get_event_loop().time())
        }
        
        # Save metadata
        safe_page_name = page_url.replace("/", "_").replace("-", "_")
        metadata_path = settings.raw_data_dir / f"page_{safe_page_name}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Page ingestion complete. Files: {len(file_paths)}")
        logger.info(f"Metadata saved to: {metadata_path}")
        
        return metadata
    
    def extract_assignment_content(self, assignment) -> Dict[str, Any]:
        """
        Extract content from a Canvas assignment.
        
        Args:
            assignment: Canvas assignment object
            
        Returns:
            Dictionary with assignment content and metadata
        """
        try:
            content = {
                "id": str(assignment.id),
                "title": assignment.name,
                "type": "assignment",
                "body": getattr(assignment, 'description', ''),
                "points_possible": getattr(assignment, 'points_possible', 0),
                "due_at": str(assignment.due_at) if hasattr(assignment, 'due_at') and assignment.due_at else None,
                "submission_types": getattr(assignment, 'submission_types', []),
                "html_url": getattr(assignment, 'html_url', ''),
            }
            
            # Add rubric if available
            if hasattr(assignment, 'rubric') and assignment.rubric:
                content['rubric'] = assignment.rubric
            
            logger.info(f"Extracted assignment: {assignment.name}")
            return content
            
        except Exception as e:
            logger.error(f"Error extracting assignment content: {e}")
            return {}
    
    async def ingest_assignment(self, course_id: str, assignment_id: int) -> Dict[str, Any]:
        """
        Ingest content from a specific Canvas assignment.
        
        Args:
            course_id: Canvas course ID
            assignment_id: Assignment ID number
            
        Returns:
            Dictionary with assignment and files data
        """
        logger.info(f"Starting ingestion for assignment ID: {assignment_id} in course {course_id}")
        
        course = self.get_course(course_id)
        
        try:
            assignment = course.get_assignment(assignment_id)
        except Exception as e:
            logger.error(f"Could not retrieve assignment {assignment_id}: {e}")
            return {}
        
        # Extract assignment content
        assignment_content = self.extract_assignment_content(assignment)
        if not assignment_content:
            logger.error(f"Could not extract content from assignment: {assignment_id}")
            return {}
        
        # Get files referenced in assignment (if any)
        download_dir = settings.raw_data_dir / "files"
        file_paths = []
        
        # Assignments might reference files in their description
        if assignment_content.get('body'):
            referenced_files = self.get_page_files(course, assignment_content['body'])
            for file in referenced_files:
                content_type = self.get_content_type(file)
                if content_type in ['application/pdf'] or content_type.startswith('image/'):
                    file_path = await self.download_file(file, download_dir)
                    if file_path:
                        file_info = {
                            "id": file.id,
                            "filename": file.filename,
                            "path": str(file_path),
                            "url": file.url,
                            "content_type": content_type,
                            "size": getattr(file, 'size', 0),
                            "type": "file"
                        }
                        file_paths.append(file_info)
        
        # Save metadata
        metadata = {
            "course_id": course_id,
            "assignment": assignment_content,
            "files": file_paths,
            "ingestion_timestamp": str(asyncio.get_event_loop().time())
        }
        
        safe_assignment_name = str(assignment_id)
        metadata_path = settings.raw_data_dir / f"assignment_{safe_assignment_name}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Assignment ingestion complete. Files: {len(file_paths)}")
        logger.info(f"Metadata saved to: {metadata_path}")
        
        return metadata
    
    async def extract_module_content(self, module, course: Course) -> Dict[str, Any]:
        """
        Extract content from a Canvas module and its items.
        
        Args:
            module: Canvas module object
            course: Canvas course object
            
        Returns:
            Dictionary with module content and metadata
        """
        try:
            module_data = {
                "id": str(module.id),
                "title": module.name,
                "type": "module",
                "position": getattr(module, 'position', 0),
                "items": []
            }
            
            # Get module items
            try:
                items = list(module.get_module_items())
                download_dir = settings.raw_data_dir / "files"
                
                for item in items:
                    item_data = {
                        "id": str(item.id),
                        "title": item.title if hasattr(item, 'title') else 'Untitled',
                        "type": item.type if hasattr(item, 'type') else 'unknown',
                        "position": getattr(item, 'position', 0),
                    }
                    
                    # Add type-specific data
                    if hasattr(item, 'url'):
                        item_data['url'] = item.url
                    if hasattr(item, 'html_url'):
                        item_data['html_url'] = item.html_url
                    if hasattr(item, 'external_url'):
                        item_data['external_url'] = item.external_url
                    if hasattr(item, 'page_url'):
                        item_data['page_url'] = item.page_url
                    
                    # Get actual content for Pages
                    if item.type == 'Page' and hasattr(item, 'page_url'):
                        try:
                            page = course.get_page(item.page_url)
                            page_content = self.extract_page_content(page)
                            if page_content:
                                item_data['content'] = page_content
                        except Exception as e:
                            logger.warning(f"Could not fetch page content for module item: {e}")
                    
                    # Download Files (PDFs, PPTx, etc.) from module items
                    elif item.type == 'File' and hasattr(item, 'url'):
                        try:
                            # Get the file object from Canvas
                            # Module items have content_id which is the file ID
                            if hasattr(item, 'content_id'):
                                file_id = item.content_id
                                file = course.get_file(file_id)
                                
                                # Download the file
                                file_path = await self.download_file(file, download_dir)
                                if file_path:
                                    item_data['file_path'] = str(file_path)
                                    item_data['filename'] = file.filename
                                    item_data['content_type'] = self.get_content_type(file)
                                    item_data['size'] = getattr(file, 'size', 0)
                                    logger.info(f"Downloaded module file: {file.filename}")
                        except Exception as e:
                            logger.warning(f"Could not download file for module item '{item.title}': {e}")
                    
                    module_data['items'].append(item_data)
                    
            except Exception as e:
                logger.warning(f"Could not get module items: {e}")
            
            logger.info(f"Extracted module: {module.name} with {len(module_data['items'])} items")
            return module_data
            
        except Exception as e:
            logger.error(f"Error extracting module content: {e}")
            return {}
    
    async def ingest_modules(self, course_id: str) -> Dict[str, Any]:
        """
        Ingest all modules from a Canvas course.
        
        Args:
            course_id: Canvas course ID
            
        Returns:
            Dictionary with all modules and their content
        """
        logger.info(f"Starting ingestion of modules for course {course_id}")
        
        course = self.get_course(course_id)
        
        try:
            modules = list(course.get_modules())
            logger.info(f"Found {len(modules)} modules")
        except Exception as e:
            logger.error(f"Could not retrieve modules: {e}")
            return {}
        
        # Extract content from each module
        module_contents = []
        for module in modules:
            module_data = await self.extract_module_content(module, course)
            if module_data:
                module_contents.append(module_data)
        
        # Save metadata
        metadata = {
            "course_id": course_id,
            "modules": module_contents,
            "ingestion_timestamp": str(asyncio.get_event_loop().time())
        }
        
        metadata_path = settings.raw_data_dir / f"modules_{course_id}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Modules ingestion complete. Total modules: {len(module_contents)}")
        logger.info(f"Metadata saved to: {metadata_path}")
        
        return metadata

async def main():
    """Main function for standalone execution."""
    course_id = settings.canvas_course_id
    if not course_id:
        logger.error("Please set CANVAS_COURSE_ID in environment variables")
        return
    
    async with CanvasIngester() as ingester:
        await ingester.ingest_course_content(course_id)

if __name__ == "__main__":
    asyncio.run(main())
