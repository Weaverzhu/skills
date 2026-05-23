---
name: arxiv-paper-reading
description: Use this skill when reading, reviewing, summarizing, explaining, auditing, or producing a paper-reading artifact for an arXiv paper. It makes local TeX source in /Users/weaverzhu/workspace/paper-readings the default evidence source and uses arxiv-downloader to fetch missing source by arXiv ID instead of browsing paper content on the web.
---

# arXiv Paper Reading

Use this skill to acquire and read arXiv papers from local TeX source. The
paper's source files, not web summaries or scraped paper text, are the evidence
base for the answer.

If a separate paper-reading or research-review workflow also applies, run this
source acquisition workflow first, then use the local source files for the
reading workflow.

## Hard Rules

- Store and reuse papers under `/Users/weaverzhu/workspace/paper-readings`.
- Prefer a user-provided arXiv ID. Accept forms like `1706.03762`,
  `arXiv:1706.03762v7`, `https://arxiv.org/abs/1706.03762`, and old-style IDs.
- If the user gives only a title, search only enough to resolve the arXiv ID.
  Do not use web pages, abstracts, PDF text, blogs, or search snippets as paper
  evidence.
- Once the arXiv ID is known, use `$arxiv-downloader` / the installed
  `arxiv-downloader` CLI to fetch missing source. Do not reimplement arXiv
  download logic.
- If a local extracted source already exists for the requested paper, read that
  source directly and do not download again unless the user asks for a fresh
  copy, asks for a specific missing version, or the source is incomplete.
- If the user asks for the latest/current version, verify or fetch the current
  version before trusting a stale local copy.
- If no TeX source is available after download, say so clearly and ask before
  falling back to PDF-derived text or web content.

## Workflow

1. **Resolve the paper identity.**
   - Extract a normalized arXiv ID from the prompt when present.
   - Preserve the version suffix when the user specifies one.
   - If no ID is present, resolve it with the smallest possible lookup:

   ```bash
   arxiv-downloader "<paper-title>" --resolve-only
   ```

   Use web search only when title resolution is ambiguous or unavailable, and
   only to find the arXiv ID.

2. **Check the local paper cache first.**
   - Look under `/Users/weaverzhu/workspace/paper-readings`.
   - Check likely directory names such as `<id>`, `arxiv-<id>`,
     `<id-with-version>`, and sanitized variants created by previous runs.
   - Confirm the directory contains useful source files such as `.tex`, `.bib`,
     `.bbl`, figure files, or extracted LaTeX dependencies.

3. **Download only when missing.**
   - Create a per-paper destination under the paper-readings root.
   - Download by arXiv ID, not by title, once the ID is known:

   ```bash
   arxiv-downloader "<arxiv-id>" --output-dir "/Users/weaverzhu/workspace/paper-readings/arxiv-<arxiv-id>"
   ```

   Follow the `$arxiv-downloader` skill for CLI behavior and flags.

4. **Read the TeX source.**
   - Identify the main TeX file by looking for `\documentclass`, title,
     abstract, `\input`, and `\include` relationships.
   - Use local files for title, abstract, introduction, method, experiments,
     figures, tables, theorems, algorithms, appendices, bibliography, and
     supplementary material.
   - Resolve included files and macros before judging technical claims.
   - Treat missing source locations as uncertainty rather than filling gaps from
     web content.

5. **Answer or produce the artifact.**
   - Ground important statements in local source locations: section, figure,
     table, theorem, algorithm, appendix, or file path when useful.
   - Separate author claims, inference from the source, and your judgment.
   - Mention the local paper directory used when it helps the user inspect the
     source.

## Local Source Checks

Useful commands:

```bash
rg --files "/Users/weaverzhu/workspace/paper-readings" | rg "<escaped-arxiv-id>"
rg --files "<paper-dir>" | rg "\.tex$|\.bib$|\.bbl$"
rg -n "\\documentclass|\\title|\\begin\\{abstract\\}|\\section|\\input|\\include" "<paper-dir>"
```

Use shell escaping appropriate to the actual ID and path. Prefer `rg` for
searching local source files.
