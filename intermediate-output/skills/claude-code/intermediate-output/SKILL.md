---
name: intermediate-output
description: Use only when the user explicitly invokes $intermediate-output or directly asks to use the intermediate-output skill. Add lightweight, inspectable module outputs for large apps, expensive workflows, or hard-to-debug systems so each small module can be checked independently before running the full system.
---

# Intermediate Output

Use this skill to reduce debugging complexity by exposing the output of one
module at a time. The goal is to create cheap, repeatable checkpoints that make
intermediate state visible without needing to run the full app or pipeline.

## Hard Constraints

- Use this skill only when the user explicitly asks for it.
- Start from the existing repo shape: inspect entrypoints, tests, scripts, and
  module boundaries before adding a harness.
- Prefer the smallest useful checkpoint over broad instrumentation.
- Keep intermediate artifacts deterministic, inspectable, and easy to rerun.
- Avoid leaking secrets, private user data, credentials, or large generated
  blobs. Redact or replace sensitive values in fixtures and snapshots.
- Do not leave noisy debug output on by default in production paths. Gate it
  behind a command, fixture, flag, test, route, or local-only script.

## Workflow

1. **Find the boundary.** Identify the smallest module whose output would
   clarify the current problem: parser output, transformed data, API payload,
   component props, generated markup, model prompt, database query result, or
   state transition.
2. **Choose the checkpoint form.** Match the output to the system:
   - CLI or script for pure functions, data transforms, prompts, and batch jobs.
   - Focused test or snapshot for stable logic and regressions.
   - Story, fixture page, or local route for UI components and visual state.
   - Local endpoint or mocked integration for server modules.
   - JSON/JSONL trace for agents, LLM calls, pipelines, and event streams.
3. **Build a thin harness.** Feed the module a small fixture, call the real code
   path where practical, and print or write the output in a stable structured
   format. Keep the harness close to existing patterns such as repo scripts,
   test helpers, fixtures, or dev routes.
4. **Run the checkpoint.** Execute only the focused command first. Inspect the
   output directly, compare it with expected shape, and fix the module before
   escalating to larger integration runs.
5. **Iterate in layers.** Add the next checkpoint only after the current module
   is understood. Use each saved output as input evidence for the next boundary.
6. **Clean up or gate.** Keep durable checkpoints that are useful for future
   debugging. Remove throwaway files, or make them clearly local/dev-only.

## Output Guidance

- Prefer structured formats: JSON for objects, JSONL for streams, text tables
  for compact human scanning, screenshots only for visual state.
- Include enough context to reproduce the output: fixture name, command,
  relevant environment flags, and input identifier.
- Keep ordering stable when snapshotting arrays, maps, logs, or generated files.
- For UI output, expose the actual component state with realistic fixture data
  instead of a marketing page or unrelated mock.
- For expensive systems, use sampled fixtures and dependency injection or mocks
  to avoid network calls, large builds, and full end-to-end runs unless needed.

## Reporting

When finished, report:

- which module boundary was exposed
- where the checkpoint or fixture lives
- the exact command, route, or test used to view it
- what the intermediate output showed
- whether the full system still needs to be run

