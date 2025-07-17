#!/usr/bin/env python3
"""Test the enhanced image query functionality specifically."""

from src.indexing.vector_store import IndexBuilder
from src.config.settings import settings

def test_image_response():
    print("Testing enhanced image response generation...")
    
    # Initialize system
    ib = IndexBuilder(embedding_model_type="openai")
    retriever = ib.get_retriever()
    
    # Test query
    prompt = "Can you show me any image from the page and provide a brief description?"
    results = retriever.retrieve(prompt, n_results=10)
    
    print(f"Found {len(results)} results")
    
    # Count images in results
    image_count = 0
    text_sources = []
    image_references = []
    
    for result in results:
        metadata = result.get("metadata", {})
        content_type = metadata.get("content_type", "text")
        text_content = result.get("text", "")
        
        if content_type == "image_reference":
            image_count += 1
            image_references.append({
                "description": text_content,
                "alt_text": metadata.get("alt_text", ""),
                "url": metadata.get("image_url", "")
            })
        else:
            text_sources.append(text_content)
    
    print(f"Images found: {image_count}")
    print(f"Text sources: {len(text_sources)}")
    
    # Show first few images
    print("\nImage references found:")
    for i, img in enumerate(image_references[:3], 1):
        print(f"  {i}. {img['description']}")
        print(f"     URL: {img['url']}")
    
    # Test the LLM prompt structure
    context_text = ""
    for i, text in enumerate(text_sources[:3]):
        context_text += f"\nSource {i+1}: {text[:100]}...\n"
    
    image_list = []
    for img in image_references[:5]:
        alt_text = f" | Alt: {img['alt_text']}" if img.get('alt_text') else ""
        image_list.append(f"- **{img['description']}**{alt_text} | URL: {img['url']}")
    
    user_prompt = f"""Question: {prompt}

Available Text Context:
{context_text}

Available Images ({len(image_references)} image references found):
{chr(10).join(image_list)}

IMPORTANT INSTRUCTIONS:
- You have access to {len(image_references)} image references from the Canvas course materials
- These images are real and available for viewing via the provided URLs
- When asked about images or visual content, you should reference these specific images
- You CAN describe what these images show based on their filenames and any alt text
- Always provide the image URLs so users can view them
- Do not say you cannot display or see images - you have image references available

Please provide a comprehensive, well-reasoned answer using the available context and image references."""

    print("\n" + "="*50)
    print("PROMPT THAT WILL BE SENT TO LLM:")
    print("="*50)
    print(user_prompt)
    print("="*50)

if __name__ == "__main__":
    test_image_response()
