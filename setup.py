"""Setup script for Canvas RAG v2."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="canvas-rag-v2",
    version="2.0.0",
    description="Multimodal RAG system for Canvas LMS architectural drawing content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Canvas RAG Team",
    author_email="",
    url="https://github.com/your-username/Canvas-RAG-v2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="rag, multimodal, canvas, lms, education, architecture, drawings",
    entry_points={
        "console_scripts": [
            "canvas-rag=src.ui.chat_app:run_app",
            "canvas-rag-pipeline=scripts.run_pipeline:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt"],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-username/Canvas-RAG-v2/issues",
        "Source": "https://github.com/your-username/Canvas-RAG-v2",
        "Documentation": "https://github.com/your-username/Canvas-RAG-v2/blob/main/README.md",
    },
)
