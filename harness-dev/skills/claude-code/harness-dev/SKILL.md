---
name: harness-dev
description: Use this skill when developing, debugging, or improving agent harnesses, evaluation loops, benchmark runners, prompt/tool orchestration, or LLM feedback systems. Trigger when Codex needs to inspect raw agent trajectories, run harness evaluations, analyze failures, reduce token waste, improve context supplied to an LLM, or iterate on harness behavior from execution traces.
---

# Harness Dev

Use this skill to improve an agent harness through a trace-first feedback loop:
export raw trajectories, inspect them, make a focused improvement, and rerun.

## Hard Constraints

- Start by verifying that the harness can export raw trajectories. If it cannot,
  implement that export first. If export is impossible from local context, ask
  the user for the missing run artifacts or harness entrypoint before tuning.
- Do not optimize from summaries alone when raw traces can be obtained.
- Preserve user data and secrets. Redact credentials before saving or sharing
  trajectories, but keep enough structure to analyze behavior.
- Keep analysis artifacts in a dedicated workspace, normally
  `.harness-dev/analysis/<timestamp>/` in the target repo unless it already has
  a convention.
- Make one or a small number of harness changes per loop so the next trajectory
  can validate the effect.

## Raw Trajectory Contract

Prefer JSON or JSONL. A useful raw trajectory should include:

- run id, task id, timestamp, harness version, command, and environment metadata
- full model input messages, system/developer instructions, tool schemas, and
  retrieved context that was visible to the model
- model outputs, tool calls, tool results, retries, errors, and final answer
- token usage, latency, costs, stop reasons, and truncation/context-window data
  when available
- scoring, labels, assertions, or human feedback used by the harness

If the current exporter is partial, document exactly what is missing and why it
matters before using the traces to guide development.

## Loop

1. **Verify export.** Locate the harness entrypoints, run commands, config, and
   existing log files. Confirm whether raw trajectories are emitted and where.
   If not, add the smallest exporter that records the raw model/tool interaction
   stream without changing harness behavior.
2. **Get trajectories.** Run the repo's maintained harness/eval commands when
   feasible. If local execution is expensive, flaky, network-bound, or requires
   unavailable credentials, ask the user for raw trajectory files.
3. **Create an analysis workspace.** Save copied traces, scripts, summaries, and
   notes under `.harness-dev/analysis/<timestamp>/`. Keep generated tooling
   there unless it is reusable enough to belong in the repo or this skill.
4. **Examine traces.** Use `scripts/summarize_trajectories.py` as a first pass,
   then manually inspect representative successes and failures. Look for missing
   context, irrelevant context, long repeated instructions, tool errors, invalid
   action formats, stale observations, hallucinated state, retry loops, scoring
   mismatches, and truncation.
5. **Develop a focused change.** Improve the harness based on trace evidence:
   trim model input, add missing state, repair parser/tool contracts, tighten
   validation, improve retry feedback, or enrich scoring diagnostics.
6. **Rerun or request the next loop.** Run the same trajectory/eval command again
   when practical. Compare before/after traces. If the user asked for multiple
   loops, start again from export and collection; otherwise report conclusions.

## Trajectory Summary Tool

Run the bundled summarizer on files or directories of trajectories:

```bash
python path/to/harness-dev/scripts/summarize_trajectories.py .harness-dev/analysis/20260517-120000/traces
```

The tool accepts JSON, JSONL, and plain text logs. Treat its output as triage,
not proof; always read the most important raw records afterward.

## Analysis Notes

In the workspace notes, record:

- trace sources and exact commands used to produce them
- exporter coverage gaps
- top failure modes with file/run references
- token/context waste and missing-context findings
- proposed harness changes and expected measurable effect
- before/after comparison when a rerun is available

## Reporting

Final responses should state:

- whether raw trajectory export exists or what was added
- which trajectories were examined and where analysis artifacts live
- the most important findings from the traces
- what harness changes were made, with local file references
- what was rerun and what changed, or why a rerun was not possible
