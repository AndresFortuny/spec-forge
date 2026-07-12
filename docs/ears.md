# EARS Notation Reference

> Easy Approach to Requirements Syntax — used for writing testable requirements.

---

## What is EARS?

EARS (Easy Approach to Requirements Syntax) is a structured way to write requirements that are:
- **Unambiguous** — no vague language
- **Testable** — every requirement can be verified
- **Complete** — covers all scenarios

## The 5 EARS Patterns

### 1. Ubiquitous (Always)
Requirements that are always true.

**Pattern:** The system shall [action].

**Example:**
- R1: The system shall validate all user input.
- R2: The system shall log all security events.

### 2. Event (When)
Requirements triggered by an event.

**Pattern:** When [event] occurs, the system shall [action].

**Example:**
- R3: When the user submits the form, the system shall validate all fields.
- R4: When the session expires, the system shall redirect to login.

### 3. State (While/During)
Requirements active during a state.

**Pattern:** While in [state], the system shall [action].

**Example:**
- R5: While processing a payment, the system shall display a loading indicator.
- R6: While in admin mode, the system shall show additional controls.

### 4. Alternative (If)
Requirements for specific conditions.

**Pattern:** If [condition], the system shall [action].

**Example:**
- R7: If the user is not authenticated, the system shall redirect to login.
- R8: If the input is invalid, the system shall display an error message.

### 5. Conflict Detection (Unless)
Requirements with exceptions.

**Pattern:** The system shall [action] unless [condition].

**Example:**
- R9: The system shall cache responses unless the user is an admin.
- R10: The system shall send notifications unless the user has opted out.

---

## Combining Patterns

Requirements can combine patterns for precision:

- **Event + State:** When [event] occurs while in [state], the system shall [action].
- **Event + Alternative:** When [event] occurs, if [condition], the system shall [action].
- **State + Alternative:** While in [state], if [condition], the system shall [action].

**Example:**
- R11: When the user submits the form while in edit mode, if validation fails, the system shall highlight the invalid fields.

---

## Writing Good EARS Requirements

### Do:
- Use "shall" for mandatory requirements
- Use "should" for recommended requirements
- Use "may" for optional requirements
- Number every requirement (R1, R2, R3...)
- Make every requirement testable
- One requirement per line

### Don't:
- Use vague language ("user-friendly", "fast", "secure")
- Combine multiple requirements in one sentence
- Use "etc." or "and so on"
- Leave room for interpretation

### Bad Examples:
- "The system shall be user-friendly." (vague)
- "The system shall validate input and log errors and send notifications." (multiple requirements)

### Good Examples:
- R1: The system shall validate all form fields within 200ms.
- R2: The system shall log all validation errors to the audit log.
- R3: The system shall send an email notification when validation fails.

---

## Traceability

Every R<n> must map to:
1. A test scenario (in `_qa_lead.md`)
2. An implementation task (in `tasks.md`)

This ensures nothing is missed and everything is verifiable.

```
R1 → TS-1 (test) → Task-1 (implementation)
R2 → TS-2 (test) → Task-2 (implementation)
```
