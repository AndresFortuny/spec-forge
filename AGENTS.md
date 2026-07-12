# spec-forge — Agent Map

> This file is a **map**, not a dump. Agents search for rules on demand.

## How to Use This File

1. Read this file first
2. Find the section relevant to your role
3. Follow the link to the detailed doc
4. Do NOT read all docs at once — progressive disclosure

---

## Roles

| Role | File | When to Activate |
|------|------|-----------------|
| **Leader** | `.claude/agents/leader.md` | Always active. Orchestrates, never implements. |
| **Business Analyst** | `.claude/agents/business_analyst.md` | When analyzing business context, stakeholders, value. |
| **Product Owner** | `.claude/agents/product_owner.md` | When defining user stories, acceptance criteria, scope. |
| **Tech Architect** | `.claude/agents/tech_architect.md` | When evaluating feasibility, dependencies, constraints. |
| **QA Lead** | `.claude/agents/qa_lead.md` | When defining test scenarios, edge cases, quality criteria. |
| **UX Designer** | `.claude/agents/ux_designer.md` | When analyzing user experience, flows, accessibility. |
| **Security Analyst** | `.claude/agents/security_analyst.md` | When identifying security requirements, compliance, threats. |

---

## Process

See `docs/process.md` for the full workflow:

```
Phase 1 (Sequential): BA → PO    (define WHAT)
Phase 2 (Parallel):   TA | QA | UX | Security  (analyze HOW)
Phase 3 (Sequential): Consolidation + Quality Gate
Phase 4 (Human):      Approval Gate
```

---

## Key Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | This file — agent map |
| `CHECKPOINTS.md` | Quality criteria for "done" |
| `feature_list.json` | Feature state tracking |
| `init.sh` | Verification script |
| `docs/process.md` | Full workflow documentation |
| `docs/ears.md` | EARS notation reference |
| `docs/stakeholder-map.md` | Stakeholder mapping template |
| `docs/quality-gates.md` | Quality gates per phase |
| `specs/<feature>/` | Output per feature |
| `progress/current.md` | Active session state |
| `progress/history.md` | Append-only log |
| `memory/decisions.md` | Architectural decisions |
| `memory/stakeholders.md` | Stakeholder map |
| `memory/patterns.md` | Established patterns |
| `memory/context.md` | Accumulated context |

---

## Rules

1. **One feature at a time** — enforced by `init.sh`
2. **State on disk, not in chat** — all results go to files
3. **Anti telephone-game** — subagents write files, return only references
4. **Human approval required** — no code without human sign-off
5. **Progressive disclosure** — read only what you need
6. **Memory is append-only** — never delete, only add with date
