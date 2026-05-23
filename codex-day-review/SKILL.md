---
name: codex-day-review
description: Review a selected day of local Codex CLI human-AI interaction and produce a standalone HTML artifact with session tables, token usage, an overlapping session timeline with drag-to-zoom, usage summary, tomorrow continuation suggestions, and high-frequency task patterns that could become skills. Use when the user asks to audit, summarize, visualize, or report on Codex CLI usage for today or a specific date.
---

# Codex Day Review

## Overview

Use this skill to generate a local HTML report from Codex CLI session data. The report defaults to today and reads from `$CODEX_HOME` or `~/.codex`, especially `sessions/**/rollout-*.jsonl` and `history.jsonl`.

## Workflow

1. Determine the target local date. Use today unless the user gives a date.
2. Resolve this skill's directory, then run the bundled script:

```bash
python3 <skill-dir>/scripts/generate_codex_day_review.py
```

3. For a specific day, pass `--date YYYY-MM-DD`:

```bash
python3 <skill-dir>/scripts/generate_codex_day_review.py --date 2026-05-20
```

4. If timezone matters, pass an IANA timezone:

```bash
python3 <skill-dir>/scripts/generate_codex_day_review.py --date 2026-05-20 --timezone Asia/Shanghai
```

5. Use `--output path/to/report.html` when the user wants the artifact in a specific location. Otherwise the script writes `codex-day-review-YYYY-MM-DD.html` in the current working directory and prints the path.

## Report Contents

The generated HTML includes:

- A session table with session ID, local time range, duration, title, token usage, model, effort, user turns, top tools, and working directory.
- An SVG timeline that places overlapping sessions on separate lanes. Drag across the graph to zoom into a time range; use the mouse wheel for centered zoom; use `Full day` to reset.
- A usage summary with total sessions, distinct active coverage, summed session time, token totals, peak overlap, busiest start hour, and tool-call count.
- Suggested tasks to continue tomorrow, inferred from recent prompts and incomplete-sounding final assistant messages.
- High-frequency task patterns that could become reusable skills, using the selected day plus a configurable `history.jsonl` lookback window.

## Script Options

- `--date YYYY-MM-DD`: local date to review; defaults to today.
- `--timezone Zone/Name`: timezone for day boundaries and display; defaults to system local timezone.
- `--codex-home PATH`: Codex home directory; defaults to `$CODEX_HOME` or `~/.codex`.
- `--output PATH`: HTML artifact path.
- `--skill-lookback-days N`: lookback window for skill-candidate frequency; defaults to 14.

## Notes

- The script uses only Python standard library modules and does not need network access.
- It includes sessions whose recorded time range overlaps the selected local day, including sessions that started on an adjacent day.
- Token usage is taken from the latest `token_count` event in each session file. If Codex log formats change, preserve the report structure and patch the parser rather than reimplementing the HTML by hand.
- The HTML contains local prompt snippets and paths. Treat the artifact as private unless the user explicitly asks to share or sanitize it.
