#!/usr/bin/env python3
"""
Z-Cred: Credit Risk Assessment Platform
A comprehensive credit scoring system using machine learning and explainable AI.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Z-Cred: Credit Risk Assessment Platform"

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    # Handle conditional dependencies
                    if ';' in line:
                        requirements.append(line)
                    else:
                        requirements.append(line)
    return requirements

setup(
    name="z-cred",
    version="1.0.0",
    author="Rizzy",
    author_email="",
    description="Credit Risk Assessment Platform using Machine Learning and Explainable AI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Rizzy1857/Z-Cred",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "z-cred-admin=src.apps.app_admin:main",
            "z-cred-user=src.apps.app_user:main",
            "z-cred=src.apps.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yml", "*.yaml"],
    },
    project_urls={
        "Bug Reports": "https://github.com/Rizzy1857/Z-Cred/issues",
        "Source": "https://github.com/Rizzy1857/Z-Cred",
        "Documentation": "https://github.com/Rizzy1857/Z-Cred/docs",
    },
)
