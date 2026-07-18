# spec-forge UI

> Web interface for visualizing, editing, and interacting with spec-forge outputs.

## Quick Start

```bash
# 1. Install dependencies (first time only)
cd ui
pip install -r requirements.txt

# 2. Copy and configure environment
cp .env.example .env
# Edit .env with your LLM provider settings

# 3. Start the server
python server.py

# 4. Open browser
# http://localhost:8000
```

## Features

- **Dashboard**: View all features and their status
- **Feature View**: See the phase pipeline and output files
- **File Editor**: Edit spec files with markdown preview
- **Memory Editor**: View and edit persistent memory
- **Agent Chat**: Chat with specialist agents for adjustments

## LLM Providers

The UI supports multiple LLM providers. Configure in `.env`:

| Provider | Default Model | Free? | Setup |
|----------|--------------|-------|-------|
| **Ollama** | qwen2.5-ctx64k | Yes (local) | Already configured |
| **OpenAI** | gpt-4 | No | Requires API key |
| **Anthropic** | claude-sonnet-4-20250514 | No | Requires API key |
| **Groq** | llama-3.3-70b-versatile | Yes (tier) | Requires free API key |
| **Gemini** | gemini-2.0-flash | Yes (tier) | Requires free API key |

## Keyboard Shortcuts

- `Ctrl+S` — Save current file
- `Escape` — Close chat panel / modal

## Architecture

```
ui/
├── server.py          # FastAPI backend
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
├── README.md          # This file
└── static/
    ├── index.html     # SPA
    ├── style.css      # Styles
    └── app.js         # Frontend logic
```
