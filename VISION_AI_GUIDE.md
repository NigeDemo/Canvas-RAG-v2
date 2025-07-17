# Canvas RAG v2 - Vision AI Integration Guide

## 🎯 Phase 2: Vision AI Capabilities

This document describes the new Vision AI integration features added to Canvas RAG v2, enabling intelligent analysis of architectural drawings using GPT-4 Vision and Claude Vision.

## 🚀 New Features

### Vision AI Providers
- **GPT-4 Vision**: Primary provider for image analysis
- **Claude Vision**: Fallback provider for enhanced reliability
- **Auto-fallback**: Seamless switching between providers

### Architectural Drawing Analysis
- **Drawing Type Detection**: Identifies floor plans, elevations, sections, details
- **Scale Analysis**: Extracts scale information and dimensions
- **Spatial Analysis**: Understands room layouts and circulation
- **Technical Analysis**: Identifies construction details and specifications
- **OCR Processing**: Extracts text, annotations, and labels

### Enhanced Features
- **Caching System**: Avoids redundant API calls
- **Batch Processing**: Analyze multiple images efficiently
- **Query-Specific Analysis**: Tailored responses based on question type
- **Comprehensive Reporting**: Detailed analysis results

## 🛠️ Quick Setup

### 1. Install Dependencies
```bash
python setup_vision_ai.py
```

### 2. Configure API Keys
Copy `.env.template` to `.env` and add your API keys:
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
CANVAS_API_TOKEN=your_canvas_api_token_here
CANVAS_COURSE_ID=your_course_id_here

# Optional (for Claude Vision fallback)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Test Integration
```bash
python test_vision_ai.py
```

### 4. Run Enhanced Chat Interface
```bash
streamlit run src/ui/vision_chat_app.py
```

## 📊 Usage Examples

### Basic Query with Vision AI
```python
from src.vision.vision_rag_integration import create_vision_rag_system

# Initialize system
vision_rag = create_vision_rag_system()

# Query with automatic image analysis
result = vision_rag.query(
    "What type of drawing is this and what are the key dimensions?",
    enable_vision=True
)

print(result.response)
```

### Direct Image Analysis
```python
from src.vision.image_analyzer import ImageAnalyzer

analyzer = ImageAnalyzer()

# Analyze architectural drawing
result = analyzer.analyze_image(
    "path/to/drawing.jpg",
    analysis_type="comprehensive"
)

print(result)
```

### OCR Text Extraction
```python
from src.vision.ocr_processor import OCRProcessor

ocr = OCRProcessor()

# Extract structured text
result = ocr.extract_structured_text("path/to/drawing.jpg")

print(f"Dimensions: {result['dimensions']}")
print(f"Room labels: {result['room_labels']}")
print(f"Scale info: {result['scale_info']}")
```

## 🏗️ Architecture

### Vision AI Pipeline
```
User Query → Query Analysis → Hybrid Search → Vision Analysis → Response Generation
     ↓              ↓              ↓              ↓              ↓
  Intent      Text Context    Image Refs    Vision Results    Enhanced Response
```

### Module Structure
```
src/vision/
├── __init__.py                 # Vision module exports
├── vision_providers.py         # GPT-4 Vision & Claude Vision
├── vision_processor.py         # Processing coordinator
├── image_analyzer.py           # Architectural analysis
├── ocr_processor.py           # Text extraction
└── vision_rag_integration.py  # Main integration
```

## ⚙️ Configuration

### Vision AI Settings
```python
# Primary and fallback providers
VISION_PRIMARY_PROVIDER=openai
VISION_FALLBACK_PROVIDER=claude

# Caching configuration
VISION_CACHE_ENABLED=true
VISION_CACHE_TTL_HOURS=24
CACHE_DIR=./data/cache

# Model specifications
OPENAI_VISION_MODEL=gpt-4o
CLAUDE_VISION_MODEL=claude-3-5-sonnet-20241022
```

### Performance Tuning
```python
# Image processing
MAX_IMAGE_SIZE=1024
PDF_DPI=200

# Analysis limits
MAX_IMAGES_PER_QUERY=3
VISION_TIMEOUT=30
```

## 🔍 Analysis Types

### 1. Drawing Type Detection
Identifies architectural drawing types:
- Floor plans
- Site plans  
- Elevations
- Sections
- Details
- Perspectives

### 2. Scale Analysis
Extracts dimensional information:
- Scale indicators (1:100, 1/4"=1'-0")
- Dimension lines and measurements
- Room sizes and areas
- Overall building dimensions

### 3. Spatial Analysis
Understands spatial relationships:
- Room layouts and organization
- Circulation patterns
- Door and window locations
- Functional zoning

### 4. Technical Analysis
Identifies construction details:
- Material specifications
- Construction methods
- Technical annotations
- Code references

### 5. OCR Processing
Extracts text content:
- Dimensions and measurements
- Room labels and identifiers
- Technical specifications
- Title block information

## 🎨 Enhanced Chat Interface

### New Features
- **Vision Toggle**: Enable/disable vision analysis
- **Direct Upload**: Analyze images directly
- **Analysis Types**: Choose specific analysis modes
- **Progress Indicators**: Real-time processing status
- **Result Details**: Comprehensive analysis breakdown

### Usage Tips
1. **Enable Vision AI** for image-related queries
2. **Upload images directly** for focused analysis
3. **Choose analysis type** based on your needs
4. **Review processing details** for insights

## 🧪 Testing

### Run All Tests
```bash
python test_vision_ai.py
```

### Test Individual Components
```python
# Test vision providers
from src.vision.vision_processor import VisionProcessor
processor = VisionProcessor()
status = processor.get_provider_status()

# Test image analysis
from src.vision.image_analyzer import ImageAnalyzer
analyzer = ImageAnalyzer()
result = analyzer.analyze_image("image.jpg", "comprehensive")

# Test OCR
from src.vision.ocr_processor import OCRProcessor
ocr = OCRProcessor()
text = ocr.extract_text("drawing.jpg")
```

## 📈 Performance Considerations

### Caching Strategy
- **Vision results cached** for 24 hours by default
- **Cache key based on** image content + prompt + provider
- **Automatic cache cleanup** for expired entries

### API Usage Optimization
- **Batch processing** for multiple images
- **Smart fallback** to reduce API costs
- **Image size optimization** before analysis
- **Token limit management** for responses

### Resource Management
- **Concurrent analysis** limited to prevent overload
- **Memory-efficient** image processing
- **Timeout handling** for long-running analyses
- **Error recovery** with graceful degradation

## 🐛 Troubleshooting

### Common Issues

#### API Key Configuration
```bash
# Check API key status
python -c "from src.config.settings import settings; print(f'OpenAI: {bool(settings.openai_api_key)}')"
```

#### Vision Provider Issues
```bash
# Test providers
python test_vision_ai.py
```

#### Image Processing Errors
```bash
# Check image format and size
python -c "from PIL import Image; img = Image.open('image.jpg'); print(f'Size: {img.size}, Format: {img.format}')"
```

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Migration from Phase 1

### Existing Code Compatibility
- **Phase 1 code continues to work** unchanged
- **New features are additive** and optional
- **Gradual migration** recommended

### Update Steps
1. **Install new dependencies**: `pip install -r requirements.txt`
2. **Add API keys**: Configure vision providers
3. **Update imports**: Use new vision-enhanced components
4. **Test integration**: Verify functionality

### Code Changes
```python
# Old (Phase 1)
from src.generation.llm_integration import RAGPipeline

# New (Phase 2)
from src.vision.vision_rag_integration import create_vision_rag_system
vision_rag = create_vision_rag_system()
```

## 📚 API Reference

### VisionProcessor
```python
class VisionProcessor:
    def analyze_image(self, image_input, prompt, **kwargs) -> Dict
    def extract_text(self, image_input, **kwargs) -> str
    def describe_image(self, image_input, **kwargs) -> str
    def batch_analyze(self, images, prompt, **kwargs) -> List[Dict]
```

### ImageAnalyzer
```python
class ImageAnalyzer:
    def analyze_image(self, image_input, analysis_type, **kwargs) -> Dict
    def batch_analyze_images(self, images, analysis_type, **kwargs) -> List[Dict]
```

### VisionEnhancedRAG
```python
class VisionEnhancedRAG:
    def query(self, query, enable_vision=True, **kwargs) -> VisionRAGResult
    def analyze_image_directly(self, image_input, query, **kwargs) -> Dict
    def extract_text_from_image(self, image_input) -> str
```

## 💡 Best Practices

### Query Optimization
- **Be specific** in your questions
- **Mention visual elements** when relevant
- **Use architectural terminology** for better results

### Image Preparation
- **High resolution** images work best
- **Clear, well-lit** photographs
- **Minimal compression** for technical drawings

### API Usage
- **Enable caching** for repeated queries
- **Use batch processing** for multiple images
- **Monitor API usage** to avoid rate limits

## 🎯 Future Enhancements

### Planned Features
- **3D model analysis** support
- **CAD file processing** capabilities
- **Interactive annotation** tools
- **Real-time collaboration** features

### Integration Roadmap
- **BIM software** integration
- **Additional vision providers**
- **Custom model training**
- **Mobile app** development

## 📞 Support

### Documentation
- **Technical details**: See `TECHNICAL.md`
- **API documentation**: See `docs/API.md`
- **Change log**: See `CHANGELOG.md`

### Community
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share ideas and get help
- **Wiki**: Community-maintained documentation

---

**Ready to explore architectural drawings with AI?** 🚀

Start with `python setup_vision_ai.py` and begin analyzing your Canvas course content with advanced vision capabilities!
