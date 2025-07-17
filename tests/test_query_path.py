#!/usr/bin/env python3
"""Test the exact query path in the chat app."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.indexing.vector_store import IndexBuilder

# Mock session state
class MockSessionState:
    def __init__(self):
        ib = IndexBuilder(embedding_model_type="openai")
        self.retriever = ib.get_retriever()

def test_query_path():
    print("Testing query path in chat app...")
    
    # Set up mock session state
    import sys
    session_state = MockSessionState()
    
    # Mock streamlit session state for the imports
    sys.modules['streamlit'] = type('MockStreamlit', (), {
        'session_state': session_state
    })()
    
    # Now import the functions
    from src.ui.chat_app import simple_query, enhanced_image_query
    
    # Test the exact query from user
    test_queries = [
        "Can you show and describe an image on the page?",
        "show me any image",
        "Can you show me any image from the page and provide a brief description?"
    ]
    
    for query in test_queries:
        print(f"\n=== Testing: '{query}' ===")
        
        # Test image detection logic
        image_keywords = ["image", "show", "visual", "picture", "drawing", "diagram", "photo", "figure", "display", "view", "see", "example"]
        is_image_query = any(keyword.lower() in query.lower() for keyword in image_keywords)
        
        image_phrases = ["show me", "can you show", "any image", "an image", "example of", "visual example"]
        is_image_phrase = any(phrase.lower() in query.lower() for phrase in image_phrases)
        
        print(f"Image keywords detected: {is_image_query}")
        print(f"Image phrases detected: {is_image_phrase}")
        print(f"Will use enhanced_image_query: {is_image_query or is_image_phrase}")
        
        # Test the actual query function
        try:
            result = simple_query(query, n_results=5)
            print(f"Query successful, image count: {result.get('image_count', 0)}")
            
            # Check if URLs are in the response
            if "https://canvas.wlv.ac.uk" in result.get('answer', ''):
                print("✅ URLs found in response")
            else:
                print("❌ No URLs found in response")
                
            # Show first 100 chars of response
            answer_preview = result.get('answer', '')[:150] + "..."
            print(f"Response preview: {answer_preview}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_query_path()
