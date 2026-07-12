# spec-forge Process

> The workflow that transforms raw requirements into development-ready specifications.

---

## Overview

```
Raw Requirement → [Analysis Pipeline] → Ready for Dev
```

The pipeline has 4 phases, using a **hybrid sequential/parallel** approach:

```
Phase 1 (Sequential): BA → PO         → define WHAT
Phase 2 (Parallel):   TA | QA | UX | Sec  → analyze HOW
Phase 3 (Sequential): Consolidation    → merge + quality gate
Phase 4 (Human):      Approval         → human signs off
```

---

## Phase 1: Business Analysis (Sequential)

### Step 1: Business Analyst

**Input:** Raw requirement from `feature_list.json`

**Actions:**
1. Read existing context from `memory/context.md`
2. Read existing stakeholders from `memory/stakeholders.md`
3. Analyze the requirement:
   - Who are the stakeholders?
   - What business value does it deliver?
   - What constraints exist?
   - Who is the target user?
4. Write findings to `memory/stakeholders.md` and `memory/context.md`

**Output:** Updated `memory/stakeholders.md` and `memory/context.md`

**Quality Gate:** Leader verifies stakeholder map and context are documented.

### Step 2: Product Owner

**Input:** BA output from `memory/`

**Actions:**
1. Read BA output
2. Define user stories (As a / I want / So that)
3. Write testable acceptance criteria for each story
4. Identify edge cases
5. Define non-functional requirements
6. Set scope boundaries (IN/OUT)
7. Write to `specs/<feature>/requirements_draft.md`

**Output:** `specs/<feature>/requirements_draft.md`

**Quality Gate:** Leader verifies all stories have testable AC and edge cases.

---

## Phase 2: Technical Analysis (Parallel)

The Leader launches 4 specialist agents **in parallel**. They are independent and can run simultaneously.

### Step 3a: Tech Architect

**Input:** PO output + `memory/decisions.md`

**Actions:**
1. Assess technical feasibility
2. Identify dependencies
3. Document constraints
4. Record architecture decisions (with alternatives)
5. Identify risks
6. Write to `specs/<feature>/_tech_architect.md`

**Output:** `specs/<feature>/_tech_architect.md`

### Step 3b: QA Lead

**Input:** PO output

**Actions:**
1. Define test scenarios for each AC
2. Identify edge cases
3. Set quality criteria with thresholds
4. Document regression risks
5. Write to `specs/<feature>/_qa_lead.md`

**Output:** `specs/<feature>/_qa_lead.md`

### Step 3c: UX Designer

**Input:** PO output + stakeholder map

**Actions:**
1. Define personas (if applicable)
2. Map user flows
3. Identify error states
4. Specify accessibility requirements
5. Write to `specs/<feature>/_ux_designer.md`

**Output:** `specs/<feature>/_ux_designer.md`

### Step 3d: Security Analyst

**Input:** PO output + tech architect output

**Actions:**
1. Classify data by sensitivity
2. Build threat model (STRIDE)
3. Define auth/authz requirements
4. Identify compliance requirements
5. Write to `specs/<feature>/_security_analyst.md`

**Output:** `specs/<feature>/_security_analyst.md`

**Quality Gate:** Leader waits for ALL 4 agents to complete before proceeding.

---

## Phase 3: Consolidation (Sequential)

### Step 4: Leader Consolidates

**Input:** All specialist outputs

**Actions:**
1. Read all `specs/<feature>/_*.md` files
2. Merge into `specs/<feature>/requirements.md` using EARS notation
3. Generate `specs/<feature>/design.md` from TA + UX + Security
4. Generate `specs/<feature>/tasks.md` as implementation checklist
5. Write new decisions to `memory/decisions.md`
6. Update `progress/current.md`
7. Update `feature_list.json` status to `spec_ready`
8. Append to `progress/history.md`

**Output:**
- `specs/<feature>/requirements.md` (EARS)
- `specs/<feature>/design.md`
- `specs/<feature>/tasks.md`
- Updated `memory/` and `progress/`

**Quality Gate:** Leader verifies all R<n> have traceability, all checkpoints in CHECKPOINTS.md are satisfied.

---

## Phase 4: Human Approval

### Step 5: Human Reviews

**Input:** All spec files

**Actions:**
1. Human reads `specs/<feature>/requirements.md`
2. Human reads `specs/<feature>/design.md`
3. Human reads `specs/<feature>/tasks.md`
4. Human approves or requests changes

**If Approved:**
- `feature_list.json` status → `done`
- Output is ready for harness-sdd or other implementation framework

**If Changes Needed:**
- `feature_list.json` status → `pending` (with notes)
- Process restarts from Phase 1

---

## File Flow

```
feature_list.json          ← Leader reads, updates status
memory/context.md          ← BA writes, Leader reads
memory/stakeholders.md     ← BA writes, Leader reads
memory/decisions.md        ← Leader writes, TA reads
specs/<feature>/requirements_draft.md  ← PO writes, Leader reads
specs/<feature>/_tech_architect.md     ← TA writes, Leader reads
specs/<feature>/_qa_lead.md            ← QA writes, Leader reads
specs/<feature>/_ux_designer.md        ← UX writes, Leader reads
specs/<feature>/_security_analyst.md   ← Sec writes, Leader reads
specs/<feature>/requirements.md        ← Leader writes (consolidated)
specs/<feature>/design.md              ← Leader writes (consolidated)
specs/<feature>/tasks.md               ← Leader writes (consolidated)
progress/current.md                    ← Leader writes
progress/history.md                    ← Leader appends
```
