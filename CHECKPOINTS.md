# CHECKPOINTS — Quality Criteria

> A feature is "done" when ALL checkpoints below are satisfied.

---

## Phase 1: Business Analysis

- [ ] Stakeholder map exists in `memory/stakeholders.md`
- [ ] Business context documented in `memory/context.md`
- [ ] Value proposition clearly stated
- [ ] Target users identified

## Phase 2: Product Definition

- [ ] User stories written with "As a [role], I want [feature], so that [benefit]"
- [ ] Acceptance criteria for each user story (testable conditions)
- [ ] Edge cases identified
- [ ] Non-functional requirements documented
- [ ] Scope boundaries defined (what's IN and what's OUT)

## Phase 3: Technical Analysis

- [ ] Technical feasibility assessed
- [ ] Dependencies identified
- [ ] Constraints documented (performance, security, compliance)
- [ ] Architecture decisions recorded in `memory/decisions.md`
- [ ] Alternative approaches considered and documented

## Phase 4: QA Analysis

- [ ] Test scenarios defined for each acceptance criterion
- [ ] Edge cases mapped to test cases
- [ ] Quality criteria established
- [ ] Regression risks identified

## Phase 5: UX Analysis

- [ ] User flows documented
- [ ] Personas defined (if applicable)
- [ ] Accessibility requirements considered
- [ ] Error states and edge cases from UX perspective

## Phase 6: Security Analysis

- [ ] Threat model documented
- [ ] Compliance requirements identified
- [ ] Data handling requirements defined
- [ ] Authentication/authorization needs specified

## Phase 7: Consolidation

- [ ] `requirements.md` uses EARS notation with R<n> numbering
- [ ] `design.md` documents decisions and alternatives
- [ ] `tasks.md` is a checklist of discrete steps
- [ ] All R<n> have traceability to tests
- [ ] Memory files updated with new decisions

## Phase 8: Human Approval

- [ ] Human has reviewed all three spec files
- [ ] Human has approved or requested changes
- [ ] Feature status updated to `spec_ready` or `pending` (if changes needed)

---

## Rejection Criteria

The reviewer MUST reject if:

1. Any checkpoint above is unchecked
2. Requirements are ambiguous or not testable
3. Acceptance criteria are not specific enough
4. Security or compliance risks are not addressed
5. Memory files are not updated with decisions
6. R<n> traceability is missing
