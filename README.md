# spec-forge

> Requirements to Ready for Dev — multi-agent framework for requirements analysis

## What Is This?

spec-forge is a **template** (not a library) that transforms raw requirements into development-ready specifications using specialized AI agents orchestrated by a leader.

**Zero dependencies.** No Python, no Node, no installation. Just markdown, JSON, and shell.

## How It Works

```
Raw Requirements → [BA → PO → TA|QA|UX|Sec → Consolidation] → Ready for Dev
```

1. **Business Analyst** understands context, stakeholders, value
2. **Product Owner** defines user stories, acceptance criteria
3. **Tech Architect**, **QA Lead**, **UX Designer**, **Security Analyst** analyze in parallel
4. **Leader** consolidates into EARS requirements, design, tasks
5. **Human** approves → output is ready for implementation

## Quick Start

```bash
# 1. Clone the template
git clone https://github.com/AndresFortuny/spec-forge.git my-project
cd my-project

# 2. Verify everything is in place
./init.sh

# 3. Open your LLM (Claude Code, Cursor, GPT, etc.)
claude

# 4. Tell the agent:
#    "Analyze the following requirement: [your requirement here]"
```

## Output

For each feature, spec-forge generates:

```
specs/<feature>/
├── requirements.md    # EARS requirements (harness-sdd compatible)
├── design.md          # Technical decisions
└── tasks.md           # Implementation checklist
```

The output is **compatible with [harness-sdd](https://github.com/betta-tech/harness-sdd)** — you can use it directly for implementation.

## Structure

```
spec-forge/
├── AGENTS.md              # Agent map (progressive disclosure)
├── CHECKPOINTS.md         # Quality criteria
├── feature_list.json      # Feature state tracking
├── init.sh                # Verification script
├── .claude/agents/        # Agent definitions (markdown)
├── docs/                  # Reference documentation
├── specs/<feature>/       # Output per feature
├── progress/              # Session state
├── memory/                # Persistent memory (human-editable)
└── ui/                    # Web UI (optional)
    ├── server.py          # FastAPI backend
    ├── static/            # Frontend (HTML/CSS/JS)
    └── README.md          # UI documentation
```

## Memory

spec-forge includes persistent memory that survives across sessions:

- `memory/decisions.md` — Architectural decisions
- `memory/stakeholders.md` — Stakeholder map
- `memory/patterns.md` — Established patterns
- `memory/context.md` — Accumulated context

**Humans can edit memory directly.** The agents read it at the start of each session.

## Web UI (Optional)

spec-forge includes an optional web interface for visualizing and editing outputs:

```bash
cd ui
pip install -r requirements.txt
cp .env.example .env  # Configure your LLM provider
python server.py
# Open http://localhost:8000
```

The UI supports:
- **Dashboard**: View all features and their status
- **Feature View**: See the phase pipeline and output files
- **File Editor**: Edit spec files with markdown preview
- **Memory Editor**: View and edit persistent memory
- **Agent Chat**: Chat with specialist agents for adjustments

LLM providers: Ollama (default, free), OpenAI, Anthropic, Groq, Gemini.

See `ui/README.md` for details.

## Compatibility

- **LLM-agnostic**: Works with Claude, GPT, Gemini, Cursor, or any markdown-capable agent
- **Framework-agnostic**: No Python, Node, or other dependencies
- **harness-sdd compatible**: Output can be consumed directly by harness-sdd
- **Web UI**: Optional web interface with multi-provider LLM support

## License

MIT
