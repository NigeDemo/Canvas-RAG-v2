#!/usr/bin/env python
"""
Simple script to set up API keys for Vision AI
"""

import os
from pathlib import Path

def setup_api_keys():
    """Set up API keys for Vision AI"""
    print("🔑 Vision AI API Key Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path(".env")
    existing_content = ""
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            existing_content = f.read()
        print(f"✅ Found existing .env file")
    else:
        print("📝 Creating new .env file")
    
    # Check what's already configured
    has_openai = "OPENAI_API_KEY" in existing_content
    has_anthropic = "ANTHROPIC_API_KEY" in existing_content
    
    print(f"OpenAI API Key: {'✅ Configured' if has_openai else '❌ Not configured'}")
    print(f"Anthropic API Key: {'✅ Configured' if has_anthropic else '❌ Not configured'}")
    
    # Ask for missing keys
    env_updates = []
    
    if not has_openai:
        print("\n🔑 OpenAI API Key Setup")
        print("1. Go to: https://platform.openai.com/api-keys")
        print("2. Create a new secret key")
        print("3. Copy the key and paste it here:")
        
        openai_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        if openai_key:
            env_updates.append(f"OPENAI_API_KEY={openai_key}")
    
    if not has_anthropic:
        print("\n🔑 Anthropic API Key Setup")
        print("1. Go to: https://console.anthropic.com/")
        print("2. Create an API key")
        print("3. Copy the key and paste it here:")
        
        anthropic_key = input("Enter your Anthropic API key (or press Enter to skip): ").strip()
        if anthropic_key:
            env_updates.append(f"ANTHROPIC_API_KEY={anthropic_key}")
    
    # Update .env file
    if env_updates:
        with open(env_file, 'a') as f:
            if existing_content and not existing_content.endswith('\n'):
                f.write('\n')
            f.write('\n# Vision AI API Keys\n')
            for line in env_updates:
                f.write(f"{line}\n")
        
        print(f"\n✅ Updated .env file with {len(env_updates)} new keys")
        print("📝 Your .env file now contains:")
        
        # Show current .env content (masked)
        with open(env_file, 'r') as f:
            for line in f:
                if 'API_KEY' in line and '=' in line:
                    key, value = line.strip().split('=', 1)
                    if value:
                        masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                        print(f"  {key}={masked_value}")
                elif line.strip():
                    print(f"  {line.strip()}")
    else:
        print("\n✅ No updates needed")
    
    print("\n🚀 Next Steps:")
    print("1. Restart your Streamlit app to load the new API keys")
    print("2. Run: streamlit run src/ui/vision_chat_app.py")
    print("3. Try uploading an image again")

if __name__ == "__main__":
    setup_api_keys()
