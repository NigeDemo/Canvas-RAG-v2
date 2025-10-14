"""Enhanced Streamlit chat interface with vision AI capabilities."""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

# Configure page
st.set_page_config(
    page_title="Canvas RAG v2 - Vision AI Architecture Assistant",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import local modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from src.config.settings import settings
    from src.vision.vision_rag_integration import create_vision_rag_system
    from src.utils.logger import get_logger
    logger = get_logger(__name__)
    
    # Optional imports for backward compatibility
    try:
        from src.retrieval.hybrid_search import HybridSearchEngine
    except ImportError:
        HybridSearchEngine = None
    
    try:
        from src.indexing.vector_store import IndexBuilder
    except ImportError:
        IndexBuilder = None
        
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()
    logger = None

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'vision_rag_system' not in st.session_state:
    st.session_state.vision_rag_system = None

if 'system_status' not in st.session_state:
    st.session_state.system_status = {}

if 'vision_enabled' not in st.session_state:
    st.session_state.vision_enabled = True


def _canvas_base_url() -> str:
    """Return the Canvas host base URL (without /api prefix)."""
    base_url = settings.canvas_api_url or ""
    if not base_url:
        return ""
    if "/api" in base_url:
        base_url = base_url.split("/api", 1)[0]
    return base_url.rstrip("/")


def _prefer_canvas_preview(url: str) -> str:
    """Convert Canvas file URLs to preview links when possible."""
    if not url:
        return ""

    # Normalize whitespace and trailing slashes but preserve querystring
    url = url.strip()

    if "/files/" not in url:
        return url

    base_part, _, query = url.partition("?")

    if "/download" in base_part:
        base_part = base_part.replace("/download", "/preview")
    elif not base_part.endswith("/preview"):
        base_part = base_part.rstrip("/") + "/preview"

    return f"{base_part}?{query}" if query else base_part


def ensure_canvas_url(url: Optional[str]) -> str:
    """Ensure URLs used in the UI resolve to the Canvas host instead of localhost."""
    if not url:
        return ""
    url = url.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return _prefer_canvas_preview(url)
    base = _canvas_base_url()
    if not base:
        return _prefer_canvas_preview(url)
    resolved = f"{base}/{url.lstrip('/')}"
    return _prefer_canvas_preview(resolved)

def initialize_vision_rag():
    """Initialize the vision-enhanced RAG system."""
    try:
        with st.spinner("Initializing Vision AI system..."):
            # Create search engine if available
            search_engine = None
            if HybridSearchEngine and IndexBuilder:
                try:
                    # Initialize index builder to get the retriever
                    index_builder = IndexBuilder(embedding_model_type="openai")
                    retriever = index_builder.get_retriever()
                    
                    # Create search engine with the retriever
                    search_engine = HybridSearchEngine(retriever)
                except Exception as e:
                    logger.warning(f"Could not initialize search engine: {e}")
            
            # Create vision RAG system
            vision_rag = create_vision_rag_system(search_engine)
            
            # Get system status
            status = vision_rag.get_system_status()
            
            st.session_state.vision_rag_system = vision_rag
            st.session_state.system_status = status
            
            st.success("✅ Vision AI system initialized successfully!")
            return True
            
    except Exception as e:
        st.error(f"❌ Error initializing Vision AI system: {e}")
        logger.error(f"Error initializing vision RAG: {e}")
        return False

def display_system_status():
    """Display system status in sidebar."""
    st.sidebar.markdown("## 🔍 System Status")
    
    status = st.session_state.get('system_status', {})
    
    if not status:
        st.sidebar.warning("System not initialized")
        return
    
    # Search engine status
    search_status = "✅ Active" if status.get('search_engine') else "❌ Inactive"
    st.sidebar.text(f"Search Engine: {search_status}")
    
    # Vision processor status
    vision_status = status.get('vision_processor', {})
    if vision_status:
        st.sidebar.text("Vision Providers:")
        for provider, provider_status in vision_status.items():
            if provider_status.get('available'):
                model = provider_status.get('model', 'unknown')
                st.sidebar.text(f"  ✅ {provider}: {model}")
            else:
                st.sidebar.text(f"  ❌ {provider}: Error")
    
    # Response generator status
    response_status = "✅ Active" if status.get('response_generator') else "❌ Inactive"
    st.sidebar.text(f"Response Generator: {response_status}")

def display_vision_controls():
    """Display vision AI controls in sidebar."""
    st.sidebar.markdown("## 🖼️ Vision AI Controls")
    
    # Vision toggle
    st.session_state.vision_enabled = st.sidebar.toggle(
        "Enable Vision AI",
        value=st.session_state.vision_enabled,
        help="Enable vision analysis of images in responses"
    )
    
    # Image upload for direct analysis
    st.sidebar.markdown("### Direct Image Analysis")
    uploaded_file = st.sidebar.file_uploader(
        "Upload image for analysis",
        type=['png', 'jpg', 'jpeg', 'gif'],
        help="Upload an architectural drawing for direct analysis"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Analysis type selection
        analysis_type = st.sidebar.selectbox(
            "Analysis Type",
            ["comprehensive", "drawing_type", "scale", "spatial", "technical", "annotations", "ocr"],
            help="Select the type of analysis to perform"
        )
        
        # Analysis button
        if st.sidebar.button("Analyze Image"):
            analyze_uploaded_image(uploaded_file, analysis_type)

def analyze_uploaded_image(uploaded_file, analysis_type):
    """Analyze uploaded image directly."""
    try:
        # Check API keys first
        if not settings.openai_api_key and not settings.anthropic_api_key:
            st.error("❌ No API keys configured. Please set up your API keys first.")
            st.info("💡 Run `python setup_api_keys.py` to configure your API keys.")
            return
        
        with st.spinner(f"Analyzing image ({analysis_type})..."):
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            
            # Read image data
            image_bytes = uploaded_file.read()
            
            # Validate image data
            if not image_bytes:
                st.error("❌ Empty image file")
                return
            
            if len(image_bytes) < 10:
                st.error("❌ Image file too small")
                return
            
            # Validate image format
            if not (image_bytes.startswith(b'\xff\xd8\xff') or  # JPEG
                    image_bytes.startswith(b'\x89PNG\r\n\x1a\n') or  # PNG
                    image_bytes.startswith(b'GIF87a') or  # GIF
                    image_bytes.startswith(b'GIF89a') or  # GIF
                    image_bytes.startswith(b'RIFF') or  # WEBP
                    image_bytes.startswith(b'BM')):  # BMP
                st.error("❌ Unsupported image format. Please use JPEG, PNG, GIF, WEBP, or BMP.")
                return
            
            # Try to open with PIL for additional validation
            try:
                image = Image.open(BytesIO(image_bytes))
                image.verify()  # Verify image integrity
                st.success(f"✅ Image loaded successfully: {image.format} {image.size}")
                
                # Reset file pointer for actual processing
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()
                
            except Exception as e:
                st.error(f"❌ Invalid image file: {e}")
                return
            
            # Get vision RAG system
            vision_rag = st.session_state.get('vision_rag_system')
            if not vision_rag:
                st.error("Vision RAG system not initialized")
                return
            
            # Perform analysis
            result = vision_rag.analyze_image_directly(
                image_bytes,
                query=f"Perform {analysis_type} analysis",
                analysis_type=analysis_type
            )
            
            # Display results
            if result.get('success', True):
                st.success("✅ Analysis completed!")
                
                # Display results based on analysis type
                if analysis_type == "comprehensive":
                    display_comprehensive_analysis(result)
                elif analysis_type == "ocr":
                    st.text_area("Extracted Text", result.get('extracted_text', ''), height=200)
                elif analysis_type == "description":
                    st.text_area("Description", result.get('description', ''), height=150)
                else:
                    # Display general analysis result
                    analysis_result = result.get('result', {})
                    if analysis_result.get('success'):
                        st.text_area("Analysis Result", analysis_result.get('analysis', ''), height=200)
                    else:
                        st.error(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")
            else:
                error_msg = result.get('error', 'Unknown error')
                st.error(f"Analysis failed: {error_msg}")
                
                # Provide helpful hints for common errors
                if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                    st.info("💡 This looks like an API key issue. Please check your API keys configuration.")
                    st.code("python setup_api_keys.py")
                
    except Exception as e:
        st.error(f"Error analyzing image: {e}")
        if "authentication" in str(e).lower() or "api_key" in str(e).lower():
            st.info("💡 This looks like an API key issue. Please run the setup script:")
            st.code("python setup_api_keys.py")

def display_comprehensive_analysis(result):
    """Display comprehensive analysis results."""
    analyses = result.get('analyses', {})
    
    for analysis_type, analysis_data in analyses.items():
        with st.expander(f"📊 {analysis_type.replace('_', ' ').title()}"):
            analysis_result = analysis_data.get('result', {})
            
            if analysis_result.get('success'):
                st.text_area(
                    f"{analysis_type} Results",
                    analysis_result.get('analysis', ''),
                    height=150,
                    key=f"analysis_{analysis_type}"
                )
            else:
                st.error(f"Failed: {analysis_result.get('error', 'Unknown error')}")

def display_chat_interface():
    """Display the main chat interface."""
    st.title("🏗️ Canvas RAG v2 - Vision AI Architecture Assistant")
    st.markdown("Ask questions about architectural drawings and get intelligent responses with visual analysis.")
    
    # Display chat history
    for i, (query, response, metadata) in enumerate(st.session_state.chat_history):
        # User message
        with st.chat_message("user"):
            st.write(query)
        
        # Assistant response
        with st.chat_message("assistant"):
            st.write(response)
            
            # Show metadata if available
            if metadata:
                with st.expander("📊 Response Details"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Processing Time", f"{metadata.get('processing_time', 0):.2f}s")
                    
                    with col2:
                        st.metric("Images Analyzed", metadata.get('images_analyzed', 0))
                    
                    with col3:
                        st.metric("Query Type", metadata.get('query_type', 'Unknown'))
                    
                    # Show vision analyses if available
                    vision_analyses = metadata.get('vision_analyses', [])
                    if vision_analyses:
                        st.markdown("**Vision Analysis Results:**")
                        for j, analysis in enumerate(vision_analyses):
                            analysis_type = analysis.get('analysis_type', 'unknown')
                            success = analysis.get('success', True)
                            status = "✅" if success else "❌"
                            st.text(f"{status} {analysis_type}")
    
    # Chat input
    if prompt := st.chat_input("Ask about architectural drawings..."):
        process_user_query(prompt)

def process_user_query(query: str):
    """Process user query with vision enhancement."""
    # Display user message
    with st.chat_message("user"):
        st.write(query)
    
    # Get vision RAG system
    vision_rag = st.session_state.get('vision_rag_system')
    if not vision_rag:
        st.error("Vision RAG system not initialized. Please initialize the system first.")
        return
    
    # Process query with loading indicator
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question and relevant images..."):
            try:
                # Process query
                result = vision_rag.query(
                    query,
                    enable_vision=st.session_state.vision_enabled,
                    max_images=3
                )
                
                # Display response
                if result.success:
                    st.write(result.response)
                    
                    # Prepare metadata for display
                    metadata = {
                        'processing_time': result.processing_time,
                        'images_analyzed': len(result.vision_analyses),
                        'query_type': result.query_type,
                        'vision_analyses': result.vision_analyses
                    }
                    
                    # Show processing details
                    if result.vision_analyses:
                        with st.expander("🔍 Vision Analysis Details"):
                            for i, analysis in enumerate(result.vision_analyses):
                                analysis_type = analysis.get('analysis_type', 'unknown')
                                success = analysis.get('success', True)
                                
                                if success:
                                    st.success(f"✅ Image {i+1}: {analysis_type} analysis completed")
                                else:
                                    st.error(f"❌ Image {i+1}: {analysis_type} analysis failed")

                    if result.image_references:
                        st.markdown("### 📷 Retrieved Canvas Images")
                        for ref in result.image_references:
                            link = ensure_canvas_url(ref.get('image_url') or ref.get('file_url') or ref.get('source_url'))
                            if not link:
                                continue

                            # Build a helpful label with sensible fallbacks
                            alt_text = (ref.get('alt_text') or "").strip()
                            page_title = (ref.get('page_title') or "").strip()
                            file_name = (ref.get('file_name') or ref.get('filename') or "").strip()
                            content_type = (ref.get('content_type') or ref.get('type') or "").strip()

                            if alt_text:
                                label = alt_text
                            elif page_title and content_type:
                                label = f"{page_title} ({content_type})"
                            elif page_title:
                                label = page_title
                            elif file_name:
                                label = file_name
                            else:
                                label = "Canvas image"

                            module = ref.get('parent_module')
                            # Compose contextual details: module, page title, filename, content type
                            context_bits = []
                            if module:
                                context_bits.append(module)
                            if page_title:
                                context_bits.append(page_title)
                            if file_name:
                                context_bits.append(file_name)
                            if content_type:
                                context_bits.append(content_type)
                            details = f" — {' | '.join(context_bits)}" if context_bits else ""

                            st.markdown(f"- [{label}]({link}){details}")
                    
                    # Add to chat history
                    st.session_state.chat_history.append((query, result.response, metadata))
                    
                else:
                    st.error(f"Error processing query: {result.error}")
                    st.session_state.chat_history.append((query, result.response, {}))
                    
            except Exception as e:
                error_msg = f"Error processing query: {e}"
                st.error(error_msg)
                st.session_state.chat_history.append((query, error_msg, {}))

def main():
    """Main application function."""
    # Sidebar
    st.sidebar.title("🏗️ Canvas RAG v2")
    st.sidebar.markdown("Vision AI Architecture Assistant")
    
    # Initialize system button
    if st.sidebar.button("🚀 Initialize Vision AI System"):
        initialize_vision_rag()
    
    # Display system status
    display_system_status()
    
    # Vision controls
    display_vision_controls()
    
    # Clear chat history
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Settings section
    with st.sidebar.expander("⚙️ Settings"):
        st.markdown("**API Configuration**")
        
        # Check API key status
        openai_key = bool(settings.openai_api_key)
        anthropic_key = bool(settings.anthropic_api_key)
        
        st.text(f"OpenAI API: {'✅ Configured' if openai_key else '❌ Missing'}")
        st.text(f"Anthropic API: {'✅ Configured' if anthropic_key else '❌ Missing'}")
        
        if not openai_key and not anthropic_key:
            st.error("❌ No API keys configured!")
            st.info("💡 Run the setup script to configure your API keys:")
            st.code("python setup_api_keys.py")
        elif not openai_key or not anthropic_key:
            st.warning("⚠️ Only one API key configured. You may experience limited functionality.")
        
        st.markdown("**Vision Settings**")
        st.text(f"Primary Provider: {settings.vision_primary_provider}")
        st.text(f"Fallback Provider: {settings.vision_fallback_provider}")
        st.text(f"Cache Enabled: {settings.vision_cache_enabled}")
        
        # API key setup button
        if st.button("🔑 Set Up API Keys"):
            st.info("Please run this command in your terminal:")
            st.code("python setup_api_keys.py")
            st.info("Then restart this Streamlit app to load the new keys.")
    
    # Main interface
    display_chat_interface()

if __name__ == "__main__":
    main()
