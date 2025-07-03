#!/usr/bin/env python3
"""
Quick start script for Canvas RAG system.
Sets up environment and runs the complete pipeline.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def check_requirements():
    """Check if required packages are installed."""
    required_packages = [
        'streamlit', 'chromadb', 'openai', 'canvasapi', 
        'pdf2image', 'Pillow', 'sentence-transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("Please copy .env.example to .env and fill in your API credentials")
        return False
    
    required_vars = [
        'CANVAS_API_URL', 'CANVAS_API_TOKEN', 'CANVAS_COURSE_ID', 'OPENAI_API_KEY'
    ]
    
    with open(env_path) as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in env_content or f"{var}=your_" in env_content or f"{var}=" in env_content.replace(f"{var}=\n", ""):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or incomplete environment variables: {', '.join(missing_vars)}")
        print("Please edit your .env file and add these values")
        return False
    
    print("✅ Environment file configured")
    return True

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup and run function."""
    print("🏗️ Canvas RAG Quick Start")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('requirements.txt').exists():
        print("❌ Please run this script from the Canvas-RAG-v2 directory")
        return
    
    # Step 1: Check requirements
    print("\n1. Checking requirements...")
    if not check_requirements():
        return
    
    # Step 2: Check environment
    print("\n2. Checking environment configuration...")
    if not check_env_file():
        return
    
    # Step 3: Run pipeline
    print("\n3. Running Canvas RAG pipeline...")
    pipeline_cmd = f"{sys.executable} scripts/run_pipeline.py"
    
    if not run_command(pipeline_cmd, "Canvas RAG pipeline"):
        print("\n❌ Pipeline failed. Check the logs above for details.")
        return
    
    # Step 4: Launch Streamlit app
    print("\n4. Launching Streamlit app...")
    print("🚀 Starting Canvas RAG chat interface...")
    print("The app will open in your browser automatically.")
    print("Press Ctrl+C to stop the application.")
    
    try:
        streamlit_cmd = f"{sys.executable} -m streamlit run src/ui/chat_app.py --server.port 8501"
        subprocess.run(streamlit_cmd, shell=True, check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start Streamlit app: {e}")

if __name__ == "__main__":
    main()
