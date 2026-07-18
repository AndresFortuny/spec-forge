/**
 * spec-forge UI — Frontend Logic
 *
 * SPA with hash-based routing.
 * Handles: features, specs, memory, agent chat.
 */

// ── State ────────────────────────────────────────────────────────────────────
let state = {
    features: [],
    currentFeature: null,
    currentFile: null,
    currentMemoryTab: 'decisions',
    chatAgent: null,
    chatFeature: null,
    chatHistory: [],
    chatSocket: null,
    editorMode: 'preview', // 'preview' or 'source'
};

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    await loadFeatures();
    handleHash();
    window.addEventListener('hashchange', handleHash);
});

// ── Routing ──────────────────────────────────────────────────────────────────
function handleHash() {
    const hash = window.location.hash || '#/';
    if (hash.startsWith('#/feature/')) {
        const name = hash.replace('#/feature/', '');
        openFeature(name);
    } else if (hash === '#/memory') {
        showMemory();
    } else {
        showDashboard();
    }
}

function navigate(hash) {
    window.location.hash = hash;
}

// ── Config ───────────────────────────────────────────────────────────────────
async function loadConfig() {
    try {
        const res = await fetch('/api/config');
        const config = await res.json();
        const badge = document.getElementById('provider-badge');
        badge.textContent = `${config.provider} / ${config.model}`;
        badge.className = 'badge badge-spec_ready';
    } catch (e) {
        console.error('Failed to load config:', e);
    }
}

// ── Features ─────────────────────────────────────────────────────────────────
async function loadFeatures() {
    try {
        const res = await fetch('/api/features');
        const data = await res.json();
        state.features = data.features || [];
        renderFeatures();
    } catch (e) {
        console.error('Failed to load features:', e);
    }
}

function renderFeatures() {
    const container = document.getElementById('features-list');
    if (state.features.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No features yet</h3>
                <p>Create your first feature to start the spec-forge process.</p>
                <button class="btn btn-primary" onclick="showNewFeature()">+ New Feature</button>
            </div>
        `;
        return;
    }

    container.innerHTML = state.features.map(f => `
        <div class="feature-card" onclick="navigate('#/feature/${f.name}')">
            <div class="feature-info">
                <h3>${escapeHtml(f.name)}</h3>
                <p>${escapeHtml(f.description || 'No description')}</p>
            </div>
            <div class="feature-meta">
                <span class="badge badge-${f.status}">${f.status}</span>
            </div>
        </div>
    `).join('');
}

// ── Views ────────────────────────────────────────────────────────────────────
function showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    const view = document.getElementById(viewId);
    if (view) view.classList.add('active');
}

function showDashboard() {
    showView('view-dashboard');
    closeChat();
    state.currentFeature = null;
    state.currentFile = null;
    navigate('#/');
}

function showMemory() {
    showView('view-memory');
    closeChat();
    loadMemory(state.currentMemoryTab);
}

// ── Feature View ─────────────────────────────────────────────────────────────
async function openFeature(name) {
    const feature = state.features.find(f => f.name === name);
    if (!feature) {
        showDashboard();
        return;
    }

    state.currentFeature = feature;
    state.currentFile = null;
    showView('view-feature');

    document.getElementById('feature-title').textContent = feature.name;
    const statusBadge = document.getElementById('feature-status');
    statusBadge.textContent = feature.status;
    statusBadge.className = `badge badge-${feature.status}`;

    // Hide editor
    document.getElementById('file-editor').style.display = 'none';

    // Render pipeline
    renderPipeline(feature);
}

function renderPipeline(feature) {
    const phases = [
        { key: 'ba', label: 'BA', agent: 'business_analyst', files: ['context.md', 'stakeholders.md'], status: 'memory' },
        { key: 'po', label: 'PO', agent: 'product_owner', files: ['requirements_draft.md'], status: 'pending' },
        { key: 'ta', label: 'TA', agent: 'tech_architect', files: ['_tech_architect.md'], status: 'pending' },
        { key: 'qa', label: 'QA', agent: 'qa_lead', files: ['_qa_lead.md'], status: 'pending' },
        { key: 'ux', label: 'UX', agent: 'ux_designer', files: ['_ux_designer.md'], status: 'pending' },
        { key: 'sec', label: 'SEC', agent: 'security_analyst', files: ['_security_analyst.md'], status: 'pending' },
        { key: 'consolidate', label: 'CONS', agent: 'leader', files: ['requirements.md', 'design.md', 'tasks.md'], status: 'pending' },
    ];

    // Determine phase statuses based on feature status and file existence
    const container = document.getElementById('phase-pipeline');
    let html = '';

    phases.forEach((phase, i) => {
        // Determine status
        let status = 'pending';
        if (feature.status === 'done') {
            status = 'done';
        } else if (feature.status === 'analyzing') {
            // Check if any of the phase files exist
            // For simplicity, mark earlier phases as done
            if (phase.key === 'ba') status = 'done';
            else if (phase.key === 'po') status = 'active';
        } else if (feature.status === 'spec_ready') {
            status = 'done';
        }

        html += `
            <div class="phase-node">
                <div class="phase-circle ${status}" onclick="openPhaseFiles('${phase.key}', '${phase.agent}', '${feature.name}', ${JSON.stringify(phase.files).replace(/"/g, '&quot;')})">
                    ${phase.key === 'consolidate' ? '&#10003;' : phase.label}
                </div>
                <span class="phase-label">${phase.label === 'CONS' ? 'Consolidate' : phase.label}</span>
            </div>
        `;

        if (i < phases.length - 1) {
            html += '<span class="phase-arrow">&rarr;</span>';
        }
    });

    container.innerHTML = html;
}

async function openPhaseFiles(phaseKey, agent, featureName, files) {
    // For memory-based phases (BA), show memory files
    if (phaseKey === 'ba') {
        showView('view-memory');
        loadMemory('context');
        return;
    }

    // For other phases, try to open the first available spec file
    for (const filename of files) {
        try {
            const res = await fetch(`/api/spec/${featureName}/${filename}`);
            if (res.ok) {
                openFileEditor(featureName, filename, agent);
                return;
            }
        } catch (e) {
            // File doesn't exist, try next
        }
    }

    // No files found — open editor with empty content
    if (files.length > 0) {
        openFileEditor(featureName, files[0], agent);
    }
}

// ── File Editor ──────────────────────────────────────────────────────────────
async function openFileEditor(feature, filename, agent) {
    state.currentFile = { feature, filename, agent };
    state.editorMode = 'preview';

    const editor = document.getElementById('file-editor');
    editor.style.display = 'block';

    document.getElementById('editor-filename').textContent = `specs/${feature}/${filename}`;

    // Load content
    let content = '';
    try {
        const res = await fetch(`/api/spec/${feature}/${filename}`);
        if (res.ok) {
            const data = await res.json();
            content = data.content;
        }
    } catch (e) {
        // File doesn't exist yet
    }

    // Set editor content
    document.getElementById('source-editor').value = content;
    renderPreview(content);

    // Update UI mode
    updateEditorMode();
}

function renderPreview(content) {
    const preview = document.getElementById('preview-content');
    if (typeof marked !== 'undefined') {
        preview.innerHTML = marked.parse(content || '');
    } else {
        preview.textContent = content || '';
    }
}

function toggleEditorMode() {
    state.editorMode = state.editorMode === 'preview' ? 'source' : 'preview';
    updateEditorMode();
}

function updateEditorMode() {
    const preview = document.getElementById('editor-preview');
    const source = document.getElementById('editor-source');

    if (state.editorMode === 'preview') {
        preview.style.display = 'block';
        source.style.display = 'none';
        renderPreview(document.getElementById('source-editor').value);
    } else {
        preview.style.display = 'none';
        source.style.display = 'block';
    }
}

async function saveFile() {
    if (!state.currentFile) return;

    const content = document.getElementById('source-editor').value;
    try {
        await fetch(`/api/spec/${state.currentFile.feature}/${state.currentFile.filename}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content }),
        });
        // Flash save indicator
        const btn = document.querySelector('.editor-actions .btn-primary');
        const original = btn.textContent;
        btn.textContent = 'Saved!';
        setTimeout(() => btn.textContent = original, 1500);
    } catch (e) {
        alert('Failed to save: ' + e.message);
    }
}

// ── Memory ───────────────────────────────────────────────────────────────────
function switchMemoryTab(tab) {
    state.currentMemoryTab = tab;
    document.querySelectorAll('.memory-tabs .tab').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tab);
    });
    loadMemory(tab);
}

async function loadMemory(tab) {
    try {
        const res = await fetch(`/api/memory/${tab}.md`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById('memory-editor').value = data.content;
        } else {
            document.getElementById('memory-editor').value = '';
        }
    } catch (e) {
        document.getElementById('memory-editor').value = '';
    }
}

async function saveMemory() {
    const content = document.getElementById('memory-editor').value;
    try {
        await fetch(`/api/memory/${state.currentMemoryTab}.md`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content }),
        });
        alert('Memory saved!');
    } catch (e) {
        alert('Failed to save: ' + e.message);
    }
}

// ── Agent Chat ───────────────────────────────────────────────────────────────
function openChat() {
    if (!state.currentFile || !state.currentFile.agent) {
        alert('No agent associated with this file.');
        return;
    }

    state.chatAgent = state.currentFile.agent;
    state.chatFeature = state.currentFile.feature;
    state.chatHistory = [];

    const panel = document.getElementById('chat-panel');
    panel.style.display = 'flex';

    const agentName = getAgentName(state.chatAgent);
    document.getElementById('chat-agent-name').textContent = `Chat with ${agentName}`;

    document.getElementById('chat-messages').innerHTML = '';
    addChatMessage('assistant', `I'm the ${agentName}. How can I help you refine this spec?`);

    // Connect WebSocket
    connectChatSocket();
}

function closeChat() {
    const panel = document.getElementById('chat-panel');
    panel.style.display = 'none';

    if (state.chatSocket) {
        state.chatSocket.close();
        state.chatSocket = null;
    }

    state.chatAgent = null;
    state.chatFeature = null;
    state.chatHistory = [];
}

function getAgentName(key) {
    const names = {
        leader: 'Leader',
        business_analyst: 'Business Analyst',
        product_owner: 'Product Owner',
        tech_architect: 'Tech Architect',
        qa_lead: 'QA Lead',
        ux_designer: 'UX Designer',
        security_analyst: 'Security Analyst',
    };
    return names[key] || key;
}

function connectChatSocket() {
    if (state.chatSocket) {
        state.chatSocket.close();
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/agent/${state.chatAgent}`;
    state.chatSocket = new WebSocket(wsUrl);

    let currentMessage = '';

    state.chatSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'token') {
            currentMessage += data.content;
            updateStreamingMessage(currentMessage);
        } else if (data.type === 'done') {
            finalizeStreamingMessage(currentMessage);
            currentMessage = '';
        } else if (data.error) {
            addChatMessage('error', data.error);
            currentMessage = '';
        }
    };

    state.chatSocket.onclose = () => {
        console.log('Chat WebSocket closed');
    };

    state.chatSocket.onerror = (e) => {
        console.error('Chat WebSocket error:', e);
    };
}

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // Add to history
    state.chatHistory.push({ role: 'user', content: message });

    // Show in UI
    addChatMessage('user', message);
    input.value = '';

    // Send to WebSocket
    if (state.chatSocket && state.chatSocket.readyState === WebSocket.OPEN) {
        startStreamingMessage();
        state.chatSocket.send(JSON.stringify({
            message: message,
            feature: state.chatFeature,
            conversation: state.chatHistory.slice(0, -1), // exclude current
        }));
    } else {
        addChatMessage('error', 'Not connected. Reconnecting...');
        connectChatSocket();
    }
}

function addChatMessage(role, content) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chat-message ${role}`;
    div.textContent = content;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function startStreamingMessage() {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'chat-message assistant';
    div.id = 'streaming-message';
    div.textContent = '...';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function updateStreamingMessage(content) {
    const el = document.getElementById('streaming-message');
    if (el) {
        el.textContent = content;
        const container = document.getElementById('chat-messages');
        container.scrollTop = container.scrollHeight;
    }
}

function finalizeStreamingMessage(content) {
    const el = document.getElementById('streaming-message');
    if (el) {
        el.id = '';
        el.textContent = content;
    }
    state.chatHistory.push({ role: 'assistant', content });
}

// ── New Feature Modal ────────────────────────────────────────────────────────
function showNewFeature() {
    document.getElementById('modal-new-feature').style.display = 'flex';
    document.getElementById('new-feature-name').focus();
}

function closeModal() {
    document.getElementById('modal-new-feature').style.display = 'none';
    document.getElementById('new-feature-name').value = '';
    document.getElementById('new-feature-desc').value = '';
}

async function createFeature(e) {
    e.preventDefault();
    const name = document.getElementById('new-feature-name').value.trim();
    const description = document.getElementById('new-feature-desc').value.trim();

    if (!name) return;

    try {
        const res = await fetch('/api/features', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description }),
        });

        if (res.ok) {
            closeModal();
            await loadFeatures();
            navigate(`#/feature/${name}`);
        } else {
            const err = await res.json();
            alert(err.detail || 'Failed to create feature');
        }
    } catch (e) {
        alert('Failed to create feature: ' + e.message);
    }
}

// ── Utils ────────────────────────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (state.currentFile) saveFile();
    }
    // Escape to close chat
    if (e.key === 'Escape') {
        closeChat();
        closeModal();
    }
});
