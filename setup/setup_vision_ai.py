#!/usr/bin/env python3
"""Setup script for Canvas RAG v2 Vision AI integration."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    # Install core requirements
    success = run_command("pip install -r requirements.txt", "Installing core dependencies")
    
    if not success:
        print("⚠️ Some dependencies may have failed to install.")
        print("Please check the output above and install missing packages manually.")
    
    return success

def create_env_template():
    """Create environment template with vision AI settings."""
    env_template = """# Canvas RAG v2 Configuration
# Copy this file to .env and fill in your actual values

# Canvas LMS Configuration
CANVAS_API_URL=https://your-canvas-instance.instructure.com/api/v1
CANVAS_API_TOKEN=your_canvas_api_token_here
CANVAS_COURSE_ID=your_course_id_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo
OPENAI_VISION_MODEL=gpt-4o

# Anthropic Configuration (for Claude Vision)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_VISION_MODEL=claude-3-5-sonnet-20241022

# Vision AI Configuration
VISION_PRIMARY_PROVIDER=openai
VISION_FALLBACK_PROVIDER=claude
VISION_CACHE_ENABLED=true
VISION_CACHE_TTL_HOURS=24

# Database Configuration
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
CHROMA_COLLECTION_NAME=canvas_multimodal

# Processing Configuration
CACHE_DIR=./data/cache
MAX_IMAGE_SIZE=1024
PDF_DPI=200
CHUNK_SIZE=512
CHUNK_OVERLAP=50
"""
    
    env_file = Path(".env.template")
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_template)
        print("✅ Created .env.template file")
        
        # Check if .env already exists
        if not Path(".env").exists():
            print("⚠️ Please copy .env.template to .env and configure your API keys")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env.template: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        "data/chroma_db",
        "data/cache",
        "data/cache/vision",
        "logs"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")

def run_tests():
    """Run vision AI integration tests."""
    print("\n🧪 Running Vision AI integration tests...")
    
    test_script = Path("test_vision_ai.py")
    if test_script.exists():
        success = run_command("python test_vision_ai.py", "Running Vision AI tests")
        return success
    else:
        print("❌ Test script not found")
        return False

def display_next_steps():
    """Display next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Canvas RAG v2 Vision AI Setup Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Configure your API keys in .env file:")
    print("   - OpenAI API key (required for GPT-4 Vision)")
    print("   - Anthropic API key (optional, for Claude Vision fallback)")
    print("   - Canvas LMS API token and course ID")
    
    print("\n2. Test the vision AI integration:")
    print("   python test_vision_ai.py")
    
    print("\n3. Run the enhanced chat interface:")
    print("   streamlit run src/ui/vision_chat_app.py")
    
    print("\n4. Or run the ingestion pipeline:")
    print("   python scripts/run_pipeline.py")
    
    print("\n📚 Documentation:")
    print("   - README.md: General setup and usage")
    print("   - TECHNICAL.md: Technical implementation details")
    print("   - docs/API.md: API documentation")
    
    print("\n🔧 Vision AI Features:")
    print("   ✅ GPT-4 Vision and Claude Vision support")
    print("   ✅ Architectural drawing analysis")
    print("   ✅ OCR text extraction")
    print("   ✅ Spatial and technical analysis")
    print("   ✅ Caching for performance")
    print("   ✅ Enhanced chat interface")

def main():
    """Main setup function."""
    print("🚀 Canvas RAG v2 - Vision AI Integration Setup")
    print("="*50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Run setup steps
    steps = [
        ("Creating directories", create_directories),
        ("Installing dependencies", install_dependencies),
        ("Creating environment template", create_env_template),
    ]
    
    for step_name, step_func in steps:
        try:
            step_func()
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            return False
    
    # Run tests if .env exists
    if Path(".env").exists():
        run_tests()
    else:
        print("⚠️ Skipping tests - please configure .env file first")
    
    # Display next steps
    display_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
