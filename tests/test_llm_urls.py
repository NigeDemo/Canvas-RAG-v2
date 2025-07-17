#!/usr/bin/env python3
"""Test to see the exact image URLs and descriptions being passed to the LLM."""

from src.indexing.vector_store import IndexBuilder
import openai
from src.config.settings import settings

def test_image_llm_call():
    print("Testing LLM call with image URLs...")
    
    # Initialize system
    ib = IndexBuilder(embedding_model_type="openai")
    retriever = ib.get_retriever()
    
    # Test query
    prompt = "show me any image"
    results = retriever.retrieve(prompt, n_results=10)
    
    # Prepare context like the chat app does
    context_text = ""
    image_references = []
    text_sources = []
    
    for i, result in enumerate(results[:10]):
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
    
    print(f"Found {len(image_references)} images:")
    for i, img in enumerate(image_references, 1):
        print(f"{i}. Description: {img['description']}")
        print(f"   URL: {img['url']}")
        print()
    
    # Test actual LLM call
    if len(image_references) > 0:
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        image_list = []
        for img in image_references[:3]:  # Just first 3 for testing
            alt_text = f" | Alt: {img['alt_text']}" if img.get('alt_text') else ""
            image_list.append(f"- **{img['description']}**{alt_text} | URL: {img['url']}")
        
        user_prompt = f"""Question: {prompt}

Available Images ({len(image_references)} image references found):
{chr(10).join(image_list)}

IMPORTANT: When mentioning any image, format it as a clickable markdown link: [Image Description](URL)
Please reference one specific image and provide its clickable URL."""

        print("="*60)
        print("SENDING TO LLM:")
        print("="*60)
        print(user_prompt)
        print("="*60)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an architectural assistant. When mentioning images, always provide clickable markdown links."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        print("LLM RESPONSE:")
        print("="*60)
        print(response.choices[0].message.content)
        print("="*60)

if __name__ == "__main__":
    test_image_llm_call()
