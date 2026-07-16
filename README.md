### **README.md**
```markdown
# ⚡ Markdown Converter

Smart text-to-Markdown converter. Save tokens in Claude, format faster.

## Features

- **Smart Detection** — auto-detects headers, lists, tasks, quotes, code blocks
- **3 Format Styles** — Claude, GitHub, Standard
- **Statistics** — tokens saved, compression ratio
- **Templates** — bug report, feature request, meeting notes, standup
- **History** — last 50 conversions stored locally

## Versions

| Version | Type | Status |
|---------|------|--------|
| [CLI](#cli) | Python CLI | ✅ Ready |
| [Web](#web) | Browser App | ✅ Ready |
| [Electron](#electron) | Desktop App | 🚧 WIP |

---

## CLI

### Install

```bash
pip install -e .
```

### Usage

```bash
# Convert file
mdconvert convert document.txt -o output.md -s

# Pipe from stdin
echo "My title\nSection:\n- item 1" | mdconvert convert -s

# Quick convert
mdconvert quick Hello World

# Use template
mdconvert template bug_report -d summary="Login broken"

# Watch clipboard
mdconvert watch-clipboard
```

### Options

```
-t, --text         Convert text directly
-o, --output       Save to file
-c, --copy         Copy to clipboard
-s, --stats        Show statistics
-f, --format       claude | github | standard
--no-smart         Disable smart detection
```

---

## Web

Open `web/index.html` in browser or:

```bash
python -m http.server 3000 -d web
```

### Features

- Pure JavaScript converter
- Dark theme
- Drag & drop files
- Keyboard shortcuts
- Local history
- Mobile responsive
- Works offline

### Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+Enter | Convert |
| Ctrl+Shift+C | Copy |
| Ctrl+H | History |
| Ctrl+K | Clear |

---

## Electron

```bash
cd electron
npm install
npm start
```

---

## Docker

```bash
docker build -t mdconvert .
docker run --rm -v $(pwd):/data mdconvert convert input.txt -o output.md -s
```

---

## How It Works

**Input:**
```
My Document
Introduction:
1. First point
2. Second point
TODO ITEMS
[ ] Task one
[x] Task two
```

**Output:**
```markdown
# My Document
## Introduction:
1. First point
2. Second point
### TODO ITEMS
- [ ] Task one
- [x] Task two
```

**Detection rules:**

| Pattern | Markdown |
|---------|----------|
| First line, <100 chars | `# H1` |
| Line ending with `:` | `## H2` |
| ALL CAPS short line | `### H3` |
| `1. Text` or `1) Text` | `1. Text` |
| `- Text` or `* Text` | `- Text` |
| `[ ] Task` or `[x] Task` | `- [ ] Task` |
| `"Long quote"` | `> Long quote` |
| `---` or `***` | `---` |

---

## Tests

```bash
pytest tests/ -v
# 62 tests passing
```

---

## Tech Stack

- **CLI:** Python 3.12, Click, Rich, PyYAML
- **Web:** Vanilla JS, CSS
- **Desktop:** Electron, electron-store
- **Testing:** pytest
- **Container:** Docker, Python 3.12-slim

---

## Project Structure

```
mdconvert/
├── mdconvert/           # Python CLI
│   ├── cli.py
│   ├── converter.py
│   ├── patterns.py
│   ├── formatters.py
│   ├── templates.py
│   ├── stats.py
│   └── config.py
├── web/                 # Web version
│   └── index.html
├── electron/            # Desktop app
│   ├── main.js
│   ├── preload.js
│   └── renderer/
├── tests/               # Tests
│   ├── test_converter.py
│   └── test_patterns.py
├── Dockerfile
└── README.md
```

---

## License

MIT
```

Сохраняю и пушу:

```bash
cat > README.md << 'EOF'
# ⚡ Markdown Converter
...
EOF

git add README.md
git commit -m "docs: add README with usage examples and project structure"
git push origin feature/web-version
```

