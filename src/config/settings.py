"""Configuration management for Canvas RAG system."""

import os
from pathlib import Path
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Canvas LMS Configuration
    canvas_api_url: str = Field(default="", env="CANVAS_API_URL")
    canvas_api_token: str = Field(default="", env="CANVAS_API_TOKEN")
    canvas_course_id: str = Field(default="", env="CANVAS_COURSE_ID")
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-vision-preview", env="OPENAI_MODEL")
    
    # Google Gemini Configuration
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-pro-vision", env="GEMINI_MODEL")
    
    # Nomic Embed Configuration
    nomic_api_key: str = Field(default="", env="NOMIC_API_KEY")
    
    # ChromaDB Configuration
    chroma_persist_directory: str = Field(default="./data/chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    chroma_collection_name: str = Field(default="canvas_multimodal", env="CHROMA_COLLECTION_NAME")
    
    # Retrieval Configuration
    dense_retrieval_top_k: int = Field(default=10, env="DENSE_RETRIEVAL_TOP_K")
    sparse_retrieval_top_k: int = Field(default=10, env="SPARSE_RETRIEVAL_TOP_K")
    hybrid_fusion_alpha: float = Field(default=0.5, env="HYBRID_FUSION_ALPHA")
    rerank_top_k: int = Field(default=5, env="RERANK_TOP_K")
    
    # Processing Configuration
    pdf_dpi: int = Field(default=200, env="PDF_DPI")
    max_image_size: int = Field(default=1024, env="MAX_IMAGE_SIZE")
    chunk_size: int = Field(default=512, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    
    # UI Configuration
    streamlit_port: int = Field(default=8501, env="STREAMLIT_PORT")
    debug_mode: bool = Field(default=True, env="DEBUG_MODE")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/canvas_rag.log", env="LOG_FILE")
    
    # Project paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = project_root / "data"
    raw_data_dir: Path = data_dir / "raw"
    processed_data_dir: Path = data_dir / "processed"
    logs_dir: Path = project_root / "logs"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.raw_data_dir.mkdir(exist_ok=True)
        self.processed_data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
