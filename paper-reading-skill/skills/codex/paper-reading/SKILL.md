---
name: paper-reading
description: Use this skill to read, summarize, review, critique, rewrite, or extract implementation details from research papers with evidence-grounded claims, source locations, and uncertainty controls. Trigger for requests involving paper triage, deep paper understanding, claim/evidence audits, literature comparison, reproducibility checks, research-use review, standalone HTML artifacts, or short blog rewrites. Do not treat "review" as conference peer review unless explicitly requested.
---

# Paper Reading

Use this skill to treat a research paper as an argument with evidence, not as text
to summarize generically.

By default, a request to "review" a paper means reviewing it for the user's own
research: understanding the field, deciding whether to trust or build on the
work, and identifying useful ideas, assumptions, gaps, and follow-up questions.
Do not simulate a conference reviewer unless the user explicitly asks for peer
review, acceptance recommendation, reviewer scores, or venue-style feedback.

## Hard Constraints

- Start from the user's reading intent: triage, deep understanding,
  implementation, standalone artifact, short blog, literature comparison, or
  research review.
- Treat "review" as a research-use review by default, not as a conference review.
  Use conference-review framing only when explicitly requested.
- Ground important statements in source locations: section, page, figure, table,
  theorem, algorithm, or appendix.
- Separate author-stated claims, inferred narrative, and your judgment.
- Ask for the paper, scope, or depth when missing information changes the answer.
- Do not assume every paper is empirical. Adapt evidence checks to paper type.
- Keep outputs concise, but preserve the method, caveats, assumptions,
  definitions, and failure modes.
- When producing an HTML artifact or other standalone reading artifact, make the
  method section self-contained and substantial enough for a reader to understand
  how the paper works without returning to the PDF.

## Workflow

1. **Establish intent.** Identify whether the user wants triage, understanding,
   implementation, standalone artifact, short blog, comparison, or research
   review. Ask one concise question only when the intent materially changes the
   work. Interpret an unqualified "review" as research review, not peer review.
2. **Build a paper card.** Capture paper type, problem, motivation, claimed
   contributions, central method, key figures/tables/theorems/algorithms, why it
   matters, and one reason to be cautious.
3. **Create a claim ledger.** Extract atomic claims before narrative summary.
   For each important claim, record claim, source location, evidence location,
   evidence type, support strength, assumptions, and caveats.
4. **Compress paragraphs when useful.** One-sentence-per-paragraph compression is
   optional and should preserve each paragraph's role in the argument. Mark
   definitions, assumptions, caveats, and experimental setup.
5. **Reconstruct the argument.** Separate author-stated narrative, inferred
   strategic angle, and reader judgment. Do not make the paper sound cleaner than
   the evidence supports.
6. **Audit evidence.** Check whether experiments, proofs, derivations, ablations,
   benchmarks, datasets, examples, or qualitative analysis support the core
   claims.
7. **Answer with checks.** Default to bottom line, paper card, core claims and
   evidence strength, reconstructed story, usefulness for the user's research,
   solid/weak/missing points, and verification questions.

## Standalone Artifacts

When asked to generate an HTML artifact, article, or similar standalone
deliverable, include the default evidence-grounded review, but do not let the
method section become a short abstract. The method section should usually be one
of the longest sections.

The method section must cover:

- input/output contract of the method
- key components, modules, variables, or mathematical objects
- step-by-step procedure or algorithmic flow
- training, inference, optimization, data construction, or proof flow as relevant
- how the method differs from baselines or prior work
- assumptions and dependencies required for the method to work
- implementation or reproduction details, including what is specified and what
  is missing

Prefer diagrams, tables, pseudocode, or numbered flows when they make the method
easier to understand. Preserve source locations for important method claims.

## Short Blog Rewrite

When the user asks for a blog, short blog, explainer, or public-facing rewrite,
produce a compact post that can stand alone for readers who have not read the
paper.

The blog should:

- start from the problem and why it matters, not from paper metadata
- define necessary terms before using them
- explain the core idea and method in plain language with a concrete example or
  analogy when useful
- summarize the main evidence and what it does or does not prove
- explain why the result matters, who should care, and where it may fail
- avoid unexplained acronyms, dangling references to section numbers, and claims
  that require reading the paper first

Keep the blog short, but not so compressed that the method becomes opaque.

## Review Modes

Default research review:

- Explain what the paper changes in the user's understanding of the field.
- Identify which claims are trustworthy enough to build on and which are not.
- Extract reusable ideas, assumptions, methods, datasets, evaluation patterns,
  and implementation details.
- Surface gaps, failure modes, and follow-up papers, checks, or experiments.
- Avoid accept/reject framing, reviewer scores, and venue-fit judgments.

Explicit peer review:

- Use only when the user asks for conference review, reviewer comments, scores,
  acceptance recommendation, rebuttal preparation, or venue-style feedback.
- Evaluate novelty, correctness, significance, clarity, evidence, and risks in
  the requested review format.

## Evidence Audit

For empirical papers, check metrics, baselines, ablations, data splits, leakage
risks, evaluation setup, statistical uncertainty, compute scale, and
reproducibility details.

For theory papers, check theorem statements, assumptions, proof dependencies,
skipped steps, examples, and whether the result applies beyond narrow regimes.

For systems, dataset, benchmark, survey, or position papers, state the evaluation
criteria first, then audit against those criteria.

## Output Rules

- Label unsupported statements as inference or unsupported.
- If only a title or abstract is available, label the output as abstract-only.
- If the user asks for a short summary, still include the central caveat and
  evidence strength.
- If the paper's claim is not supported by its evidence, say so directly.
- Prefer concise conclusions, assumptions, and checks over long hidden reasoning.

## Claim Ledger Template

```text
Claim: ...
Source: section/page/figure/table/appendix ...
Evidence: ...
Evidence type: experiment/proof/ablation/benchmark/dataset/example/analysis
Support: strong/partial/weak/unsupported/not checked
Assumptions and caveats: ...
```
