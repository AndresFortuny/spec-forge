# Quality Gates

> Quality criteria that must be satisfied before moving to the next phase.

---

## Phase 1 → Phase 2: Business Analysis Complete

**Gate:** Leader verifies BA output

- [ ] Stakeholder map exists in `memory/stakeholders.md`
- [ ] At least one stakeholder identified
- [ ] Business context documented in `memory/context.md`
- [ ] Problem statement is clear and specific
- [ ] Target users identified
- [ ] Value proposition stated
- [ ] Constraints documented (if any)

**If gate fails:** BA must complete missing items before PO starts.

---

## Phase 2 → Phase 3: Product Definition Complete

**Gate:** Leader verifies PO output

- [ ] At least one user story defined
- [ ] All user stories follow format: "As a [role], I want [feature], so that [benefit]"
- [ ] Every user story has testable acceptance criteria
- [ ] Edge cases identified for each story
- [ ] Non-functional requirements documented
- [ ] Scope boundaries explicit (IN/OUT)
- [ ] BA context incorporated

**If gate fails:** PO must complete missing items before technical analysis.

---

## Phase 3 → Phase 4: Technical Analysis Complete

**Gate:** Leader verifies ALL specialist outputs

- [ ] `_tech_architect.md` exists with feasibility assessment
- [ ] `_qa_lead.md` exists with test scenarios
- [ ] `_ux_designer.md` exists with user flows
- [ ] `_security_analyst.md` exists with threat model
- [ ] All dependencies identified
- [ ] All risks documented with mitigations
- [ ] All security requirements in EARS format

**If gate fails:** Missing specialist outputs must be completed before consolidation.

---

## Phase 4 → Human Approval: Consolidation Complete

**Gate:** Leader verifies consolidated output

### requirements.md
- [ ] Uses EARS notation
- [ ] All requirements numbered (R1, R2, R3...)
- [ ] Every R<n> is testable
- [ ] No vague language
- [ ] Traceability to tests documented

### design.md
- [ ] Architecture decisions documented
- [ ] Alternatives considered
- [ ] Rationale for each decision
- [ ] Impact on project documented

### tasks.md
- [ ] Checklist format
- [ ] Tasks are discrete and actionable
- [ ] Every R<n> maps to at least one task
- [ ] Tasks are ordered logically

### Memory Updated
- [ ] New decisions written to `memory/decisions.md`
- [ ] New patterns written to `memory/patterns.md`
- [ ] Context updated in `memory/context.md`

**If gate fails:** Consolidation must be redone with missing items.

---

## Human Approval Gate

**Gate:** Human reviews and approves

- [ ] Human has read `requirements.md`
- [ ] Human has read `design.md`
- [ ] Human has read `tasks.md`
- [ ] Human approves OR requests changes

**If approved:** Status → `done`. Output ready for implementation.

**If changes needed:** Status → `pending`. Process restarts from Phase 1.

---

## Rejection Criteria

The reviewer MUST reject if:

1. Any checkpoint above is unchecked
2. Requirements are ambiguous or not testable
3. Acceptance criteria are not specific enough
4. Security or compliance risks are not addressed
5. Memory files are not updated with decisions
6. R<n> traceability is missing
7. Multiple features are in `analyzing` state (violates one-at-a-time rule)
