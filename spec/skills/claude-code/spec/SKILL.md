---
name: spec
description: Use this skill when maintaining specs inside a git codebase, especially to capture, clarify, and preserve the user's implementation intent before code changes. Trigger for requests to write, update, reconcile, or review specs, plans, requirements, acceptance criteria, or implementation notes in a repository.
---

# Spec

Use this skill to maintain specs as durable records of the user's intent. A spec
should make future implementation decisions easier by preserving goals,
constraints, tradeoffs, and acceptance criteria that are otherwise easy to lose.

## Hard Constraints

- Start from the repo: inspect existing specs, code shape, conventions, and git
  state before asking questions.
- Treat the user's intent as the source of truth. Do not replace unresolved
  preferences with invented requirements.
- Keep specs concise, explicit, and implementation-ready.
- Do not edit production code, run migrations, or implement the feature unless
  the user explicitly asks for execution.
- Preserve existing spec content unless it is superseded, contradicted, or made
  obsolete by the user's current intent.
- Mark assumptions, defaults, open questions, and out-of-scope items clearly.

## Workflow

1. **Ground in the repo.** Read relevant specs, manifests, schemas, entrypoints,
   tests, and nearby implementation before drafting changes.
2. **Extract intent.** Capture the user's goal, audience, success criteria,
   constraints, non-goals, and important tradeoffs.
3. **Resolve ambiguity.** Prefer repo facts over questions. Ask only when a
   missing preference materially changes the spec.
4. **Update the spec.** Write the smallest durable update that records intent and
   gives an implementer enough direction to proceed without guessing.
5. **Check consistency.** Reconcile names, APIs, data flow, edge cases, tests,
   rollout notes, and compatibility constraints with the surrounding repo.
6. **Report changes.** Summarize what intent was recorded, any assumptions made,
   and any open questions that remain.

## Spec Content

Include these sections when they are relevant to the change:

- Goal and user intent
- Current state and discovered constraints
- Proposed behavior or design
- Public interfaces, schemas, commands, or file formats
- Edge cases and failure modes
- Acceptance criteria and test scenarios
- Migration, rollout, or compatibility notes
- Open questions and explicit assumptions

Omit sections that would only add boilerplate. Prefer precise bullets over broad
process language.

## Maintenance Rules

- If a spec already exists, update it in place when the topic is the same.
- If multiple specs conflict, preserve both facts and add a short reconciliation
  note instead of silently choosing one.
- If the user changes their mind, record the new decision and remove or mark the
  old decision as superseded.
- If implementation has drifted from the spec, document the drift and whether
  the spec or code appears to be the intended source of truth.
- For reviews, lead with gaps that would cause implementation mistakes: missing
  intent, ambiguous interfaces, untestable criteria, or contradictions.

## Output Rules

- Keep final answers short and focused on the spec changes.
- Cite local files when explaining where intent was recorded.
- When no file changes are needed, state the current spec status and why.
