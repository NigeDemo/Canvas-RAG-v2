# Vision AI Setup Guide

## 🎉 Phase 2: Vision AI Integration Complete!

Your Canvas RAG v2 system now includes comprehensive vision AI capabilities with GPT-4 Vision and Claude Vision integration.

## ✅ What's Been Implemented

### Core Vision AI Modules
- **VisionProcessor**: Main coordinator for image analysis and caching
- **VisionProviders**: GPT-4 Vision (primary) and Claude Vision (fallback) 
- **ImageAnalyzer**: Specialized architectural drawing analysis
- **OCRProcessor**: Text extraction from architectural drawings
- **VisionEnhancedResponseGenerator**: Enhanced responses with vision context
- **VisionEnhancedRAG**: Complete integration with existing RAG system

### Features
- **Multi-provider support**: GPT-4 Vision primary, Claude Vision fallback
- **Intelligent caching**: Avoids redundant API calls
- **Architectural analysis**: Specialized for building plans, sections, elevations
- **OCR extraction**: Dimensions, room labels, technical specifications
- **Enhanced UI**: Streamlit interface with image upload and analysis

## 🔧 Next Steps - Choose Your Usage Mode

The Vision AI system works in **two modes**:

### Mode 1: Direct Image Analysis (Ready Now!)
Upload and analyze images directly through the web interface:

```bash
# Set up API keys first
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Run the vision chat app
streamlit run src/ui/vision_chat_app.py
```

**No pipeline required!** Upload any architectural drawing and start asking questions.

### Mode 2: Canvas Content + Vision (Requires Pipeline)
To analyze images that are already in your Canvas LMS content:

#### 1. Set up Environment Variables
Create a `.env` file in your project root:

```env
# Vision AI API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Canvas API credentials (for ingesting Canvas content)
CANVAS_API_URL=your_canvas_url
CANVAS_API_KEY=your_canvas_key
```

#### 2. Run the Canvas Pipeline
```bash
# Run the full pipeline to ingest and process Canvas content
python scripts/run_pipeline.py

# Or run specific steps
python scripts/run_pipeline.py --skip-ingestion  # Skip if already ingested
python scripts/run_pipeline.py --page-url "specific_page_url"  # Single page
```

#### 3. Use the Enhanced System
After running the pipeline, your Canvas content (including images) will be searchable with vision AI.

### 2. Get API Keys

#### OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key to your `.env` file

#### Anthropic API Key
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Copy the key to your `.env` file

## 🚀 Quick Start Guide

### Option A: Test Vision AI Immediately
If you want to test the vision capabilities right now:

```bash
# Test the vision system (no Canvas content needed)
python test_vision_system.py

# Run the vision chat app
streamlit run src/ui/vision_chat_app.py
```

Upload any architectural drawing and ask questions about it!

### Option B: Full Canvas Integration
If you want to analyze Canvas content with vision AI:

1. **Set up Canvas API credentials** in your `.env` file
2. **Run the ingestion pipeline**:
   ```bash
   python scripts/run_pipeline.py
   ```
3. **Use the integrated system** - your Canvas content will now include vision analysis

## 🔄 Pipeline Information

**Do you need to run the pipeline?**
- **For direct image upload**: ❌ No, just run the Streamlit app
- **For Canvas content analysis**: ✅ Yes, run `python scripts/run_pipeline.py`

The existing pipeline already handles:
- Canvas content ingestion
- Image extraction from PDFs
- Text processing
- Vector indexing

The Vision AI enhances this by adding intelligent image analysis on top of the existing processed content.

## 📊 System Status

Run this to check system status:
```bash
python test_fixes.py
```

Current status:
- ✅ All core modules installed and working
- ✅ OpenAI Vision provider ready (needs API key)
- ⚠️ Claude Vision provider ready (needs API key)
- ✅ Enhanced UI ready for image upload
- ✅ Caching system operational
- ✅ Integration with existing RAG system

## 🎯 Usage Examples

### Via Python API
```python
from src.vision.vision_rag_integration import VisionEnhancedRAG

# Initialize system
vision_rag = VisionEnhancedRAG()

# Text-only query
result = vision_rag.query("What are line weights in architectural drawings?")

# Image analysis query
result = vision_rag.query(
    "Analyze this floor plan", 
    image_urls=["path/to/your/image.jpg"]
)
```

### Via Web Interface
1. Run: `streamlit run src/ui/vision_chat_app.py`
2. Upload architectural images
3. Ask questions about the drawings
4. Get vision-enhanced responses

## 🛠️ Architecture Overview

```
Canvas RAG v2 + Vision AI
├── Text Processing (Phase 1 - Complete)
│   ├── Canvas API Integration
│   ├── Content Processing
│   └── Vector Search
└── Vision AI (Phase 2 - Complete)
    ├── Image Analysis
    ├── OCR Processing
    ├── Multi-provider Vision
    └── Enhanced Response Generation
```

## 🎊 Success!

Your Canvas RAG v2 system now has complete Vision AI integration! The system can:
- Analyze architectural drawings and plans
- Extract text and dimensions from images
- Provide enhanced responses combining text and visual context
- Handle both GPT-4 Vision and Claude Vision APIs
- Cache results for efficiency
- Provide a beautiful web interface for interaction

Configure your API keys and start exploring the enhanced capabilities!
