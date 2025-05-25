#!/usr/bin/env python3
"""
Setup script for xPOURY4 Recon
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="xPOURY4-recon",
    version="1.0.0",
    author="xPOURY4",
    author_email="xpoury4@proton.me",
    description="Elite Cyber Intelligence & Digital Forensics Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xPOURY4/xPOURY4-recon",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "xpourya4-recon=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "xPOURY4_recon": [
            "web/templates/*.html",
        ],
    },
    keywords="osint, reconnaissance, cybersecurity, intelligence, forensics, github, domain, phone, linkedin, shodan",
    project_urls={
        "Bug Reports": "https://github.com/xPOURY4/xPOURY4-recon/issues",
        "Source": "https://github.com/xPOURY4/xPOURY4-recon",
        "Documentation": "https://github.com/xPOURY4/xPOURY4-recon#readme",
    },
) 