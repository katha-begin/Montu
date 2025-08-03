#!/usr/bin/env python3
"""
Montu Manager Ecosystem Setup Configuration
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Montu Manager Ecosystem - DCC-agnostic file, task, and media management system"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name="montu-manager",
    version="0.1.0",
    description="DCC-agnostic file, task, and media management ecosystem for VFX/animation studios",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Montu Development Team",
    author_email="dev@montu-manager.com",
    url="https://github.com/katha-begin/Montu",
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    python_requires=">=3.8",
    install_requires=read_requirements(),
    
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'pytest-qt>=4.2.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.5.0',
        ],
        'docs': [
            'sphinx>=7.1.0',
            'sphinx-rtd-theme>=1.3.0',
        ],
        'build': [
            'PyInstaller>=5.13.0',
            'setuptools>=68.0.0',
            'wheel>=0.41.0',
        ]
    },
    
    entry_points={
        'console_scripts': [
            'montu-launcher=montu.project_launcher.main:main',
            'montu-task-creator=montu.task_creator.main:main',
            'montu-review=montu.review_app.main:main',
            'montu-cli=montu.cli.main:main',
        ],
    },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
    ],
    
    keywords="vfx animation pipeline dcc maya nuke project-management version-control",
    
    project_urls={
        "Bug Reports": "https://github.com/katha-begin/Montu/issues",
        "Source": "https://github.com/katha-begin/Montu",
        "Documentation": "https://montu-manager.readthedocs.io/",
    },
    
    include_package_data=True,
    zip_safe=False,
)
