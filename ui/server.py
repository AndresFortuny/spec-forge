"""
spec-forge UI — FastAPI Backend

Serves the web UI and provides API endpoints for:
- Feature management
- Spec file read/write
- Memory file read/write
- Agent chat (streaming via WebSocket)
- Phase triggering
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# ── Load environment ──────────────────────────────────────────────────────────
load_dotenv()

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "..")).resolve()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# ── LLM Configuration ────────────────────────────────────────────────────────
LLM_CONFIGS = {
    "ollama": {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "api_key": "ollama",
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5-ctx64k"),
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.getenv("GROQ_API_KEY", ""),
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    },
}

# ── Agent definitions ─────────────────────────────────────────────────────────
AGENTS_DIR = PROJECT_ROOT / ".claude" / "agents"
AGENTS = {
    "leader": {"name": "Leader", "description": "Orchestrator"},
    "business_analyst": {"name": "Business Analyst", "description": "Business context, stakeholders"},
    "product_owner": {"name": "Product Owner", "description": "User stories, acceptance criteria"},
    "tech_architect": {"name": "Tech Architect", "description": "Feasibility, dependencies"},
    "qa_lead": {"name": "QA Lead", "description": "Test scenarios, quality"},
    "ux_designer": {"name": "UX Designer", "description": "User experience, flows"},
    "security_analyst": {"name": "Security Analyst", "description": "Security, compliance"},
}

# ── Allowed file operations ───────────────────────────────────────────────────
ALLOWED_SPEC_FILES = {
    "requirements.md", "requirements_draft.md", "design.md", "tasks.md",
    "_tech_architect.md", "_qa_lead.md", "_ux_designer.md", "_security_analyst.md",
}
ALLOWED_MEMORY_FILES = {"decisions.md", "stakeholders.md", "patterns.md", "context.md"}


# ── Helpers ───────────────────────────────────────────────────────────────────
def read_file(path: Path) -> str:
    """Read a file safely."""
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path.name}")
    return path.read_text(encoding="utf-8")


def write_file(path: Path, content: str) -> None:
    """Write a file safely."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def get_llm_config():
    """Get current LLM configuration."""
    config = LLM_CONFIGS.get(LLM_PROVIDER, LLM_CONFIGS["ollama"])
    return {**config, "provider": LLM_PROVIDER}


# ── FastAPI App ───────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    print(f"spec-forge UI starting...")
    print(f"  Project root: {PROJECT_ROOT}")
    print(f"  LLM Provider: {LLM_PROVIDER}")
    print(f"  LLM Model: {get_llm_config()['model']}")
    yield
    print("spec-forge UI stopped.")


app = FastAPI(title="spec-forge UI", lifespan=lifespan)

# Serve static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ── Routes: Static ───────────────────────────────────────────────────────────
@app.get("/")
async def index():
    """Serve the main SPA."""
    return FileResponse(str(static_dir / "index.html"))


# ── Routes: API ───────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "ok", "provider": LLM_PROVIDER, "model": get_llm_config()["model"]}


@app.get("/api/config")
async def config():
    """Get LLM configuration (without secrets)."""
    cfg = get_llm_config()
    return {
        "provider": cfg["provider"],
        "model": cfg["model"],
        "available_providers": list(LLM_CONFIGS.keys()),
    }


@app.get("/api/features")
async def list_features():
    """List all features from feature_list.json."""
    fl_path = PROJECT_ROOT / "feature_list.json"
    if not fl_path.exists():
        return {"features": [], "project": "unknown"}
    data = json.loads(fl_path.read_text(encoding="utf-8"))
    return data


@app.post("/api/features")
async def create_feature(body: dict):
    """Create a new feature."""
    fl_path = PROJECT_ROOT / "feature_list.json"
    data = json.loads(fl_path.read_text(encoding="utf-8")) if fl_path.exists() else {"features": []}

    name = body.get("name", "").strip()
    description = body.get("description", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Feature name is required")

    new_id = max((f.get("id", 0) for f in data["features"]), default=0) + 1
    from datetime import date
    feature = {
        "id": new_id,
        "name": name,
        "description": description,
        "status": "pending",
        "sdd": True,
        "created_at": date.today().isoformat(),
        "notes": "",
    }
    data["features"].append(feature)
    fl_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Create specs directory
    specs_dir = PROJECT_ROOT / "specs" / name
    specs_dir.mkdir(parents=True, exist_ok=True)

    return feature


@app.put("/api/features")
async def update_features(body: dict):
    """Update feature_list.json (full replace)."""
    fl_path = PROJECT_ROOT / "feature_list.json"
    fl_path.write_text(json.dumps(body, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"status": "ok"}


@app.get("/api/spec/{feature}/{filename}")
async def get_spec_file(feature: str, filename: str):
    """Read a spec file for a feature."""
    if filename not in ALLOWED_SPEC_FILES:
        raise HTTPException(status_code=400, detail=f"File not allowed: {filename}")
    path = PROJECT_ROOT / "specs" / feature / filename
    content = read_file(path)
    return {"content": content, "path": str(path.relative_to(PROJECT_ROOT))}


@app.put("/api/spec/{feature}/{filename}")
async def save_spec_file(feature: str, filename: str, body: dict):
    """Save a spec file for a feature."""
    if filename not in ALLOWED_SPEC_FILES:
        raise HTTPException(status_code=400, detail=f"File not allowed: {filename}")
    path = PROJECT_ROOT / "specs" / feature / filename
    write_file(path, body.get("content", ""))
    return {"status": "ok", "path": str(path.relative_to(PROJECT_ROOT))}


@app.get("/api/spec/{feature}")
async def list_spec_files(feature: str):
    """List all spec files for a feature."""
    specs_dir = PROJECT_ROOT / "specs" / feature
    if not specs_dir.exists():
        return {"files": []}
    files = [f.name for f in specs_dir.iterdir() if f.is_file() and f.name != ".gitkeep"]
    return {"files": sorted(files)}


@app.get("/api/memory/{filename}")
async def get_memory_file(filename: str):
    """Read a memory file."""
    if filename not in ALLOWED_MEMORY_FILES:
        raise HTTPException(status_code=400, detail=f"File not allowed: {filename}")
    path = PROJECT_ROOT / "memory" / filename
    content = read_file(path)
    return {"content": content, "path": f"memory/{filename}"}


@app.put("/api/memory/{filename}")
async def save_memory_file(filename: str, body: dict):
    """Save a memory file."""
    if filename not in ALLOWED_MEMORY_FILES:
        raise HTTPException(status_code=400, detail=f"File not allowed: {filename}")
    path = PROJECT_ROOT / "memory" / filename
    write_file(path, body.get("content", ""))
    return {"status": "ok"}


@app.get("/api/progress/{feature}")
async def get_progress(feature: str):
    """Get progress for a feature."""
    path = PROJECT_ROOT / "progress" / "current.md"
    content = read_file(path) if path.exists() else ""
    return {"content": content}


@app.get("/api/agents")
async def list_agents():
    """List available agents."""
    result = []
    for key, info in AGENTS.items():
        agent_file = AGENTS_DIR / f"{key}.md"
        exists = agent_file.exists()
        result.append({**info, "key": key, "exists": exists})
    return {"agents": result}


@app.get("/api/agents/{agent_key}")
async def get_agent(agent_key: str):
    """Get agent definition."""
    if agent_key not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_key}")
    path = AGENTS_DIR / f"{agent_key}.md"
    content = read_file(path)
    return {"content": content, "info": AGENTS[agent_key]}


@app.post("/api/phase/start")
async def start_phase(body: dict):
    """Start a phase for a feature."""
    feature = body.get("feature", "")
    phase = body.get("phase", "")
    agent_key = body.get("agent", "")

    if not feature or not agent_key:
        raise HTTPException(status_code=400, detail="feature and agent are required")

    # Update feature status
    fl_path = PROJECT_ROOT / "feature_list.json"
    if fl_path.exists():
        data = json.loads(fl_path.read_text(encoding="utf-8"))
        for f in data["features"]:
            if f["name"] == feature:
                f["status"] = "analyzing"
                break
        fl_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Create specs directory
    specs_dir = PROJECT_ROOT / "specs" / feature
    specs_dir.mkdir(parents=True, exist_ok=True)

    return {"status": "ok", "feature": feature, "phase": phase, "agent": agent_key}


# ── WebSocket: Agent Chat ────────────────────────────────────────────────────
@app.websocket("/ws/agent/{agent_key}")
async def agent_chat(websocket: WebSocket, agent_key: str):
    """Stream agent chat via WebSocket."""
    await websocket.accept()

    if agent_key not in AGENTS:
        await websocket.send_json({"error": f"Agent not found: {agent_key}"})
        await websocket.close()
        return

    # Load agent definition
    agent_file = AGENTS_DIR / f"{agent_key}.md"
    if not agent_file.exists():
        await websocket.send_json({"error": f"Agent definition not found: {agent_key}"})
        await websocket.close()
        return

    agent_prompt = agent_file.read_text(encoding="utf-8")

    # Load memory context
    memory_context = ""
    for mem_file in ["context.md", "stakeholders.md", "decisions.md", "patterns.md"]:
        mem_path = PROJECT_ROOT / "memory" / mem_file
        if mem_path.exists():
            content = mem_path.read_text(encoding="utf-8")
            if content.strip():
                memory_context += f"\n\n## {mem_file}\n{content}"

    # Load current feature specs if provided
    spec_context = ""

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("message", "")
            feature = data.get("feature", "")
            conversation = data.get("conversation", [])

            # Load feature specs if provided
            spec_context = ""
            if feature:
                specs_dir = PROJECT_ROOT / "specs" / feature
                if specs_dir.exists():
                    for f in specs_dir.iterdir():
                        if f.is_file() and f.suffix == ".md":
                            content = f.read_text(encoding="utf-8")
                            if content.strip():
                                spec_context += f"\n\n## specs/{feature}/{f.name}\n{content}"

            # Build messages
            messages = [
                {"role": "system", "content": f"{agent_prompt}\n\n---\n\n## Memory Context{memory_context}{spec_context}"}
            ]

            # Add conversation history
            for msg in conversation:
                messages.append({"role": msg["role"], "content": msg["content"]})

            messages.append({"role": "user", "content": user_message})

            # Stream response from LLM
            config = get_llm_config()
            full_response = ""

            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    if config["provider"] == "anthropic":
                        # Anthropic API format
                        system_msg = messages[0]["content"]
                        chat_messages = messages[1:]
                        payload = {
                            "model": config["model"],
                            "max_tokens": 4096,
                            "system": system_msg,
                            "messages": chat_messages,
                            "stream": True,
                        }
                        headers = {
                            "x-api-key": config["api_key"],
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json",
                        }
                        url = f"{config['base_url']}/messages"

                    elif config["provider"] == "gemini":
                        # Gemini API format (simplified)
                        contents = []
                        for msg in messages:
                            role = "user" if msg["role"] == "user" else "model"
                            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
                        payload = {
                            "contents": contents,
                            "generationConfig": {"maxOutputTokens": 4096},
                        }
                        headers = {"Content-Type": "application/json"}
                        url = f"{config['base_url']}/models/{config['model']}:streamGenerateContent?key={config['api_key']}"

                    else:
                        # OpenAI-compatible format (Ollama, OpenAI, Groq)
                        payload = {
                            "model": config["model"],
                            "messages": messages,
                            "max_tokens": 4096,
                            "stream": True,
                        }
                        headers = {
                            "Authorization": f"Bearer {config['api_key']}",
                            "Content-Type": "application/json",
                        }
                        url = f"{config['base_url']}/chat/completions"

                    async with client.stream("POST", url, json=payload, headers=headers) as response:
                        if response.status_code != 200:
                            error_body = await response.aread()
                            await websocket.send_json({
                                "error": f"LLM API error ({response.status_code}): {error_body.decode()[:500]}"
                            })
                            continue

                        async for line in response.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break

                            try:
                                chunk = json.loads(data_str)

                                # Extract token based on provider
                                token = ""
                                if config["provider"] in ("openai", "ollama", "groq"):
                                    if "choices" in chunk and chunk["choices"]:
                                        delta = chunk["choices"][0].get("delta", {})
                                        token = delta.get("content", "")
                                elif config["provider"] == "anthropic":
                                    if chunk.get("type") == "content_block_delta":
                                        token = chunk.get("delta", {}).get("text", "")
                                elif config["provider"] == "gemini":
                                    if "candidates" in chunk and chunk["candidates"]:
                                        parts = chunk["candidates"][0].get("content", {}).get("parts", [])
                                        if parts:
                                            token = parts[0].get("text", "")

                                if token:
                                    full_response += token
                                    await websocket.send_json({
                                        "type": "token",
                                        "content": token,
                                    })
                            except json.JSONDecodeError:
                                continue

            except httpx.TimeoutException:
                await websocket.send_json({"error": "LLM request timed out"})
            except httpx.ConnectError:
                await websocket.send_json({
                    "error": f"Cannot connect to {config['provider']}. Is it running?"
                })
            except Exception as e:
                await websocket.send_json({"error": str(e)})

            # Send completion signal
            await websocket.send_json({"type": "done", "content": full_response})

    except WebSocketDisconnect:
        pass


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
