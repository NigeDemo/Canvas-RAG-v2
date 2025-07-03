"""Streamlit chat interface for Canvas RAG system."""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, Any, List
import time

# Configure page
st.set_page_config(
    page_title="Canvas RAG - Architecture Drawing Assistant",
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
    from src.indexing.vector_store import IndexBuilder
    from src.utils.logger import get_logger
    logger = get_logger(__name__)
    
    # Optional imports - may not exist yet
    try:
        from src.retrieval.hybrid_search import HybridSearchEngine
    except ImportError:
        HybridSearchEngine = None
    
    try:
        from src.generation.llm_integration import RAGPipeline
    except ImportError:
        RAGPipeline = None
        
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()
    logger = None  # Fallback

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None

if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False

def initialize_system():
    """Initialize the RAG system."""
    try:
        with st.spinner("Loading Canvas RAG system..."):
            # Check if index exists
            processed_files = list(settings.processed_data_dir.glob("processed_*.json"))
            
            if not processed_files:
                st.error("""
                No processed content found. Please run the ingestion and processing pipeline first:
                
                1. Set up your `.env` file with Canvas API credentials
                2. Run: `python scripts/run_pipeline.py`
                """)
                return False
            
            # Initialize index builder with existing components
            index_builder = IndexBuilder(embedding_model_type="openai")
            
            # Get the hybrid retriever (this includes both vector and sparse search)
            retriever = index_builder.get_retriever()
            st.session_state.retriever = retriever
            st.session_state.system_ready = True
            
            safe_log("info", "System initialized successfully")
            return True
            
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        safe_log("error", f"System initialization error: {e}")
        return False

def display_chat_message(role: str, content: str, sources: List[Dict] = None):
    """Display a chat message with sources."""
    with st.chat_message(role):
        st.write(content)
        
        if sources and role == "assistant":
            with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
                for i, source in enumerate(sources, 1):
                    st.markdown(f"""
                    **{i}. {source['title']}** ({source['type']})
                    - Relevance: {source['score']:.3f}
                    - Snippet: {source['snippet']}
                    {f"- [View Source]({source['url']})" if source.get('url') else ""}
                    """)

def display_query_analysis(analysis: Dict[str, Any]):
    """Display query analysis in sidebar."""
    with st.sidebar:
        st.subheader("🔍 Query Analysis")
        
        st.write(f"**Question Type:** {analysis.get('question_type', 'unknown')}")
        st.write(f"**Intent:** {analysis.get('intent', 'unknown')}")
        
        if analysis.get('is_visual_query'):
            st.write("🖼️ **Visual Query Detected**")
        
        if analysis.get('drawing_types'):
            st.write(f"**Drawing Types:** {', '.join(analysis['drawing_types'])}")
        
        if analysis.get('keywords'):
            st.write(f"**Key Terms:** {', '.join(analysis['keywords'][:5])}")

def enhanced_image_query(prompt: str, n_results: int = 10) -> Dict[str, Any]:
    """Enhanced query specifically for image-related requests."""
    try:
        retriever = st.session_state.retriever
        
        # First, try to get some images specifically
        image_results = retriever.vector_store.query(
            retriever.embedding_manager.embed_query("image visual example drawing"),
            n_results=10,
            where={"content_type": "image_reference"}
        )
        
        # Then get regular hybrid results
        regular_results = retriever.retrieve(prompt, n_results=n_results)
        
        # Combine results, prioritizing images for image queries
        combined_results = []
        
        # Add image results first if we got any
        if image_results and image_results.get("documents"):
            for i, (doc, meta, dist, doc_id) in enumerate(zip(
                image_results["documents"][0],
                image_results["metadatas"][0], 
                image_results["distances"][0],
                image_results["ids"][0]
            )):
                combined_results.append({
                    "text": doc,
                    "metadata": meta,
                    "score": 1.0 - dist,  # Convert distance to similarity score
                    "rank": i + 1,
                    "id": doc_id
                })
        
        # Add regular results
        for result in regular_results:
            if result not in combined_results:  # Avoid duplicates
                combined_results.append(result)
        
        # Limit to n_results
        combined_results = combined_results[:n_results]
        
        return generate_llm_response(prompt, combined_results, n_results)
        
    except Exception as e:
        safe_log("error", f"Enhanced image query error: {e}")
        # Fallback to regular search (without calling simple_query to avoid circular reference)
        retriever = st.session_state.retriever
        fallback_results = retriever.retrieve(prompt, n_results=n_results)
        return generate_llm_response(prompt, fallback_results, n_results)

def simple_query(prompt: str, n_results: int = 10) -> Dict[str, Any]:
    """Enhanced query function using hybrid retriever + LLM reasoning."""
    try:
        # Get hybrid retriever from session state (combines dense vector + sparse BM25 search)
        retriever = st.session_state.retriever
        
        # Check if this is an image-related query
        image_keywords = ["image", "show", "visual", "picture", "drawing", "diagram", "photo", "figure", "display", "view", "see", "example"]
        is_image_query = any(keyword.lower() in prompt.lower() for keyword in image_keywords)
        
        # Also check for phrases that indicate image requests
        image_phrases = ["show me", "can you show", "any image", "an image", "example of", "visual example"]
        is_image_phrase = any(phrase.lower() in prompt.lower() for phrase in image_phrases)
        
        if is_image_query or is_image_phrase:
            # For image queries, try to get more images in results
            safe_log("info", f"Detected image query: '{prompt}' - using enhanced image retrieval")
            return enhanced_image_query(prompt, n_results)
        else:
            # Perform regular hybrid search
            safe_log("info", f"Regular query: '{prompt}' - using standard retrieval")
            results = retriever.retrieve(prompt, n_results=n_results)
            return generate_llm_response(prompt, results, n_results)
        
    except Exception as e:
        safe_log("error", f"Query error: {e}")
        return {
            "answer": f"Error processing query: {str(e)}",
            "sources": [],
            "total_sources": 0
        }

def generate_llm_response(prompt: str, context_results: List[Dict], n_results: int = 10) -> Dict[str, Any]:
    """Generate an intelligent response using OpenAI with the retrieved context."""
    try:
        import openai
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        # Prepare context from search results
        context_text = ""
        image_references = []
        text_sources = []
        
        for i, result in enumerate(context_results[:n_results]):
            metadata = result.get("metadata", {})
            content_type = metadata.get("content_type", "text")
            text_content = result.get("text", "")
            
            if content_type == "image_reference":
                image_references.append({
                    "description": text_content,
                    "alt_text": metadata.get("alt_text", ""),
                    "url": metadata.get("image_url", "")
                })
            else:
                text_sources.append(text_content)
                context_text += f"\nSource {i+1}: {text_content}\n"
        
        # Create system prompt for architectural drawing assistant
        system_prompt = """You are an expert architectural drawing assistant with deep knowledge of construction drawings, technical specifications, building design, and architectural standards. 

Your role is to provide clear, accurate, and educational responses about architectural drawings, construction techniques, building codes, and design principles.

IMPORTANT: You have access to both text content AND image references from Canvas course materials. When image references are provided in the context, you CAN and SHOULD:
- Describe the images based on their descriptions and alt text
- Reference specific images by their descriptions
- Provide URLs for users to view the actual images (ALWAYS include the full URL when mentioning an image)
- Explain what the images show and their relevance

When answering:
1. Provide comprehensive explanations with proper reasoning
2. Reference specific details from the provided context
3. Explain technical concepts in an accessible way
4. When relevant, mention industry standards (RIBA stages, drawing scales, line weights, etc.)
5. If images are available, actively reference them, describe them, and ALWAYS provide their full URLs
6. Structure your response logically with clear sections when appropriate
7. When asked to show images, provide the image descriptions and full clickable URLs from the context
8. Format URLs as markdown links: [Image Name](URL) to make them clickable

Always base your response on the provided context, but synthesize and explain rather than just quoting. You ARE able to reference and describe images when they are provided in the context."""

        # Create user prompt with context
        image_list = []
        for img in image_references[:10]:
            alt_text = f" | Alt: {img['alt_text']}" if img.get('alt_text') else ""
            image_list.append(f"- **{img['description']}**{alt_text} | URL: {img['url']}")
        
        user_prompt = f"""Question: {prompt}

Available Text Context:
{context_text}

Available Images ({len(image_references)} image references found):
{chr(10).join(image_list)}

IMPORTANT INSTRUCTIONS FOR YOUR RESPONSE:
- You have access to {len(image_references)} image references from the Canvas course materials
- These images are real and available for viewing via the provided URLs
- When asked about images or visual content, you should reference these specific images
- You CAN describe what these images show based on their filenames and any alt text
- ALWAYS provide the image URLs as clickable markdown links: [Image Description](URL)
- Do not say you cannot display or see images - you have image references available
- Include the full URL for each image you mention in your response

Please provide a comprehensive, well-reasoned answer using the available context and image references. When mentioning any image, format it as a clickable link."""

        # Generate response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        # Format sources for display
        sources = []
        for i, result in enumerate(context_results):
            metadata = result.get("metadata", {})
            sources.append({
                "title": metadata.get("source", f"Document {i+1}"),
                "type": metadata.get("content_type", "text"),
                "score": result.get("score", 0),
                "snippet": result.get("text", "")[:200] + "...",
                "url": metadata.get("image_url") if metadata.get("content_type") == "image_reference" else None
            })
        
        return {
            "answer": answer,
            "sources": sources,
            "total_sources": len(context_results),
            "has_images": len(image_references) > 0,
            "image_count": len(image_references)
        }
        
    except Exception as e:
        safe_log("error", f"LLM generation error: {e}")
        # Fallback to simple response
        return simple_query_fallback(prompt, context_results)

def simple_query_fallback(prompt: str, results: List[Dict]) -> Dict[str, Any]:
    """Fallback function when LLM generation fails."""
    # Format sources
    sources = []
    for i, result in enumerate(results):
        metadata = result.get("metadata", {})
        sources.append({
            "title": metadata.get("source", f"Document {i+1}"),
            "type": metadata.get("content_type", "text"),
            "score": result.get("score", 0),
            "snippet": result.get("text", "")[:200] + "...",
            "url": metadata.get("image_url") if metadata.get("content_type") == "image_reference" else None
        })
    
    # Create a simple answer from the top results
    answer = f"Based on the available content, here are the most relevant results:\n\n"
    
    for i, result in enumerate(results[:3], 1):
        answer += f"{i}. {result.get('text', '')[:300]}...\n\n"
    
    return {
        "answer": answer,
        "sources": sources,
        "total_sources": len(results)
    }

def safe_log(level: str, message: str):
    """Safe logging function."""
    if logger:
        getattr(logger, level)(message)
    else:
        print(f"[{level.upper()}] {message}")

def main():
    """Main application."""
    
    # Header
    st.title("🏗️ Canvas RAG - Architecture Drawing Assistant")
    st.markdown("Ask questions about architectural drawings and design from your Canvas course materials.")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")
        
        if not st.session_state.system_ready:
            if st.button("🚀 Initialize System", type="primary"):
                if initialize_system():
                    st.rerun()
        else:
            st.success("✅ System Ready")
            
            # System info
            st.subheader("📊 System Info")
            if st.session_state.get('retriever'):
                try:
                    vector_info = st.session_state.retriever.vector_store.get_collection_info()
                    st.write(f"**Documents Indexed:** {vector_info.get('count', 0)}")
                    st.write(f"**Collection:** {vector_info.get('name', 'Unknown')}")
                except Exception as e:
                    st.write(f"**Status:** System loaded (info unavailable)")
            
            # Settings
            st.subheader("🔧 Settings")
            n_results = st.slider("Number of search results", 5, 20, 10)
            show_debug = st.checkbox("Show debug info", value=False)
            
            if st.button("🔄 Reset Chat"):
                st.session_state.chat_history = []
                st.rerun()
    
    # Main chat interface
    if not st.session_state.system_ready:
        st.warning("Please initialize the system using the button in the sidebar.")
        return
    
    # Display chat history
    for message in st.session_state.chat_history:
        display_chat_message(
            message["role"], 
            message["content"], 
            message.get("sources")
        )
    
    # Chat input
    if prompt := st.chat_input("Ask about architectural drawings, scales, techniques, etc."):
        
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user", 
            "content": prompt
        })
        
        # Display user message
        display_chat_message("user", prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching Canvas materials and generating intelligent response..."):
                try:
                    # Query using our enhanced function with LLM reasoning
                    response = simple_query(prompt, n_results=n_results)
                    
                    # Display answer
                    st.write(response['answer'])
                    
                    # Display additional info if images were found
                    if response.get('has_images'):
                        st.info(f"🖼️ Found {response.get('image_count', 0)} relevant images in the search results.")
                    
                    # Display sources
                    sources = response.get('sources', [])
                    if sources:
                        with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
                            for i, source in enumerate(sources, 1):
                                content_type = source['type']
                                if content_type == "image_reference":
                                    st.markdown(f"""
                                    **{i}. 🖼️ {source['title']}** (Image Reference)
                                    - Relevance: {source['score']:.3f}
                                    - Content: {source['snippet']}
                                    {f"- [View Image]({source['url']})" if source.get('url') else ""}
                                    """)
                                else:
                                    st.markdown(f"""
                                    **{i}. 📄 {source['title']}** (Text)
                                    - Relevance: {source['score']:.3f}
                                    - Snippet: {source['snippet']}
                                    """)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response['answer'],
                        "sources": sources
                    })
                    
                    # Display debug info if requested
                    if show_debug:
                        with st.expander("🐛 Debug Information", expanded=False):
                            st.write(f"**Total Sources Found:** {response.get('total_sources', 0)}")
                            st.write(f"**Images Found:** {response.get('image_count', 0)}")
                            st.write(f"**LLM Reasoning Used:** {not 'Based on the available content, here are the most relevant results:' in response.get('answer', '')}")
                            
                            # Debug image detection
                            image_keywords = ["image", "show", "visual", "picture", "drawing", "diagram", "photo", "figure", "display", "view", "see", "example"]
                            is_image_query = any(keyword.lower() in prompt.lower() for keyword in image_keywords)
                            image_phrases = ["show me", "can you show", "any image", "an image", "example of", "visual example"]
                            is_image_phrase = any(phrase.lower() in prompt.lower() for phrase in image_phrases)
                            
                            st.write(f"**Image Query Detected:** {is_image_query or is_image_phrase}")
                            st.write(f"**Keywords Match:** {is_image_query}")
                            st.write(f"**Phrases Match:** {is_image_phrase}")
                            
                            st.json(response)
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    safe_log("error", f"Chat error: {e}")

def run_app():
    """Run the Streamlit app."""
    main()

if __name__ == "__main__":
    run_app()
