from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mdconvert",
    version="1.0.0",
    author="Your Name",
    author_email="your@email.com",
    description="Smart Markdown converter for Claude token optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/mdconvert",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.1.0",
        "rich>=13.7.0",
        "pyperclip>=1.8.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0",
            "pytest-cov>=4.0",
            "black>=24.0",
            "mypy>=1.8",
            "ruff>=0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "mdconvert=mdconvert.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
)