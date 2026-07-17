# ⚡ Markdown Converter (CLI)

Smart text-to-Markdown converter for Claude token optimization.

## Install

```bash
pip install -e .
Usage
bash
# Convert file
mdconvert convert document.txt -o output.md -s

# Pipe from stdin
echo "My title\nSection:\n- item 1" | mdconvert convert -s

# Quick convert
mdconvert quick Hello World

# Interactive mode
mdconvert convert
Options
Flag	Description
-t, --text	Convert text directly
-o, --output	Save to file
-c, --copy	Copy to clipboard
-s, --stats	Show statistics
--no-smart	Disable smart detection
How It Works
Input:

text
My Document
Introduction:
1. First point
TODO ITEMS
[ ] Task one
Output:

markdown
# My Document
## Introduction:
1. First point
### TODO ITEMS
- [ ] Task one
Tests
bash
pytest tests/ -v
# 62 tests
Docker
bash
docker build -t mdconvert .
docker run --rm -v $(pwd):/data mdconvert convert input.txt -o output.md -s
More Versions
Web: feature/web-version

VSCode: feature/vscode-extension
EOF
