#!/usr/bin/env python3
"""
JAGAPADI v2.2 - AI Deteksi Hama Padi
Setup script untuk instalasi otomatis
"""

from setuptools import setup, find_packages
import os
import sys

# Baca README untuk long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Baca requirements dari file
def read_requirements(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f 
                if line.strip() and not line.startswith("#") and not line.startswith("-")]

# Base requirements
install_requires = [
    "pywebview>=4.4.1",
    "pycryptodome>=3.19.0",
    "ultralytics>=8.0.196",
    "Pillow>=10.0.1",
    "opencv-python>=4.8.1.78",
    "torch>=2.0.1",
    "torchvision>=0.15.2",
    "numpy>=1.24.3",
]

# Optional requirements untuk fitur tambahan
extras_require = {
    "dev": [
        "pytest>=7.4.2",
        "black>=23.7.0",
        "flake8>=6.0.0",
        "jupyter>=1.0.0",
        "sphinx>=7.1.2",
    ],
    "gpu": [
        "torch>=2.0.1",  # CUDA version
        "torchvision>=0.15.2",  # CUDA version
    ],
    "minimal": [
        "pywebview>=4.4.1",
        "pycryptodome>=3.19.0",
        "ultralytics>=8.0.196",
        "Pillow>=10.0.1",
        "opencv-python>=4.8.1.78",
    ]
}

# Platform-specific dependencies
if sys.platform.startswith("win"):
    # Windows-specific packages
    extras_require["windows"] = []
elif sys.platform.startswith("linux"):
    # Linux-specific packages
    extras_require["linux"] = []
elif sys.platform.startswith("darwin"):
    # macOS-specific packages
    extras_require["macos"] = []

setup(
    name="jagapadi",
    version="2.2.0",
    author="PENS Team",
    author_email="developer@pens.ac.id",
    description="AI-powered Rice Pest Detection System",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pens-team/jagapadi",
    project_urls={
        "Bug Tracker": "https://github.com/pens-team/jagapadi/issues",
        "Documentation": "https://github.com/pens-team/jagapadi/wiki",
        "Source Code": "https://github.com/pens-team/jagapadi",
    },
    
    # Package configuration
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "jagapadi": [
            "ui_2/*.html",
            "ui_2/*.css", 
            "ui_2/*.js",
            "model/*.pt",
            "*.json",
            "*.md",
        ],
    },
    
    # Requirements
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    
    # Entry points untuk command line
    entry_points={
        "console_scripts": [
            "jagapadi-server=server:start_server",
            "jagapadi-client=client_2:start_client",
            "jagapadi=client_2:start_client",  # Default entry point
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Desktop Environment",
        "Natural Language :: Indonesian",
    ],
    
    # Keywords
    keywords="ai, machine-learning, object-detection, yolo, agriculture, pest-detection, rice, computer-vision",
    
    # Additional metadata
    zip_safe=False,
    platforms=["any"],
    
    # Dependencies links (jika ada)
    dependency_links=[
        "https://download.pytorch.org/whl/cpu/",
        "https://download.pytorch.org/whl/cu118/",  # CUDA 11.8
    ],
)