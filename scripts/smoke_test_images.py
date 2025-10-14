"""
Quick smoke test for image queries through the Vision RAG system.
Runs a few representative queries and prints a compact summary.
"""
import os
import sys

# Ensure project root is on PYTHONPATH
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.vision.vision_rag_integration import create_vision_rag_system
from src.retrieval.hybrid_search import HybridSearchEngine
from src.indexing.vector_store import IndexBuilder

QUERIES = [
    "List all images from this Canvas topic",
    "Show me images about steel frames",
    "What drawings are available for Session 5?",
]

def main():
    try:
        index_builder = IndexBuilder(embedding_model_type="openai")
        retriever = index_builder.get_retriever()
        search_engine = HybridSearchEngine(retriever)
        rag = create_vision_rag_system(search_engine)
    except Exception as e:
        print("INIT ERROR:", e)
        return 1

    for q in QUERIES:
        try:
            result = rag.query(q, enable_vision=True, max_images=10)
            print("QUERY:", q)
            print("SUCCESS:", result.success)
            print("IMAGES:")
            for ref in result.image_references:
                label = ref.get('alt_text') or ref.get('page_title') or ref.get('file_name') or ref.get('filename') or 'Canvas image'
                print(" -", label, "->", ref.get('image_url') or ref.get('file_url') or ref.get('source_url'))
            # Print first 200 chars of response for brevity
            print("RESPONSE:", (result.response or "")[:200].replace('\n', ' '), "...")
            print("-"*60)
        except Exception as e:
            print("ERROR running query:", q)
            print(" ", e)
            print("-"*60)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
