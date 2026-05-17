# Paper Reading Skill Workflow

## Goal

Help an LLM generate durable paper-reading artifacts as evidence work, not as
generic summarization or general paper Q&A. The output should make the paper
easier to understand, but it must preserve where claims come from, how strongly
they are supported, and what remains uncertain.
The artifact should be self-contained enough that a technically appropriate
reader understands the paper after reading the artifact without needing to read
the original paper first. Treat the artifact as a shorter, clearer version of
the paper with evidence and caveats preserved, not as notes taken after reading
the paper.
This workflow is scoped to artifacts such as HTML reports, Markdown reports,
articles, blog/explainers, structured reading artifacts, claim/evidence audits,
literature-comparison reports, reproducibility reports, and implementation-notes
documents.
Do not use this skill for ordinary paper Q&A, chat-style explanations, isolated
factual questions, quick summaries, paper lookup, citation lookup, or brief
clarification.
By default, a request to "review" a paper means reviewing it for the user's own
research: understanding the field, deciding whether to trust or build on the
work, and identifying useful ideas, assumptions, gaps, and follow-up questions.
Do not simulate a conference reviewer unless the user explicitly asks for peer
review, acceptance recommendation, reviewer scores, or venue-style feedback.

## Hard Constraints

- Only invoke this workflow when the user wants a paper-reading artifact or
  deliverable. For general Q&A on papers, answer normally without applying this
  workflow.
- Start from the user's reading intent: triage, deep understanding,
  implementation notes, standalone artifact, short blog, literature comparison,
  reproducibility report, or research review artifact.
- Treat "review" as a research-use review by default, not as a conference review.
  Use conference-review framing only when explicitly requested.
- Ground important statements in paper locations such as section, page, figure,
  table, theorem, algorithm, or appendix.
- Separate author-stated claims from inferred narrative and external judgment.
- Prefer asking for the missing paper, scope, or depth over silently inventing
  context.
- Do not assume every paper is empirical. Theory, system, benchmark, dataset,
  position, survey, and negative-result papers need different evidence checks.
- Keep final outputs concise, but do not compress away the method, caveats,
  assumptions, definitions, or failure modes.
- Write artifacts for readers who have not read the paper. The artifact must
  carry the paper's problem, method, claims, evidence, limitations, and practical
  meaning as a coherent shorter substitute, not as a checklist of reading notes.
- When producing an HTML artifact or other standalone reading artifact, make the
  method section self-contained and substantial enough for a reader to understand
  how the paper works without returning to the PDF.

## First-Principles Model

A paper is an argument with evidence.

The core objects are:

- Problem: what question or gap the paper targets.
- Claim: what the authors say is true or useful.
- Evidence: experiment, proof, derivation, benchmark, dataset, ablation, example,
  or qualitative analysis used to support a claim.
- Assumption: what must be true for the claim to hold.
- Contribution: what changes for the reader if the claim is accepted.
- Limitation: what the paper does not show, cannot show, or leaves ambiguous.

The workflow should build from these objects rather than from summary style.

## Workflow

### 1. Establish Reading Intent

Before detailed reading, confirm that the user wants an artifact and choose
depth. If the user only asks a general question about a paper, do not use this
workflow.

Artifact goals include:

- Triage: decide whether the paper is worth reading.
- Understanding: explain the paper's argument and technical mechanism.
- Implementation notes: extract reproducible details, algorithms, settings, and
  missing information.
- Standalone artifact: write an HTML or Markdown explanation that a reader
  can use to understand the paper without reading the original paper first.
- Short blog: rewrite the paper into a compact, self-contained blog post for
  technically literate readers who have not read the paper.
- Literature comparison: position the paper against prior and follow-up work.
- Research review: evaluate what the paper teaches about the field, whether its
  claims are trustworthy, what ideas are reusable, what assumptions matter, what
  gaps remain, and what follow-up reading or experiments would clarify it.
- Peer review: only when explicitly requested, evaluate novelty, correctness,
  evidence, clarity, significance, and venue-fit; include scores or acceptance
  recommendation only if asked.

If the goal is unclear and affects the output, ask one concise question.

### 2. First Pass: Paper Card

Produce a compact card:

- bibliographic facts if available
- paper type
- problem and motivation
- claimed contributions
- central method or idea
- key figures, tables, theorems, algorithms, or appendices
- one-sentence reason the paper might matter
- one-sentence reason to be cautious

### 3. Claim Ledger

Extract atomic claims before writing the narrative summary.

For each important claim, record:

- claim
- source location
- evidence location
- evidence type
- support strength: strong, partial, weak, unsupported, or not checked
- assumptions and caveats

This ledger is the main hallucination control surface. If no location supports a
claim, label it as inference or unsupported.

### 4. Paragraph Compression

Use one-sentence-per-paragraph compression only after the paper structure and
claims are known.

Each sentence should preserve the paragraph's role in the argument, not merely
paraphrase it. Mark paragraphs that introduce definitions, assumptions, caveats,
or experimental setup because those are easy to lose during compression.

### 5. Argument Reconstruction

Reconstruct the paper's story in three layers:

- Author-stated narrative: what the paper explicitly says.
- Inferred angle: the strategic framing that makes the work publishable, such as
  a new constraint, benchmark, simplification, dataset, theoretical lens, or
  systems tradeoff.
- Reader judgment: whether the story is actually supported by the claim ledger.

Avoid making the paper sound cleaner than it is.

### 6. Evidence Audit

Evaluate whether evidence supports the core claims.

For empirical papers, check:

- metrics and whether they match the claimed goal
- baselines and whether they are fair/current
- ablations and whether they isolate the proposed contribution
- data splits, leakage risks, evaluation setup, and statistical uncertainty
- compute, scale, and implementation details needed to reproduce results

For theory papers, check:

- theorem statements against assumptions
- proof dependencies and skipped steps
- whether examples match the theorem's intended use
- whether the result applies to realistic cases or only narrow regimes

For systems, dataset, benchmark, survey, or position papers, adapt the audit to
the paper type and state the criteria used.

### 7. Final Artifact

Default artifact structure:

1. Bottom line.
2. Paper card.
3. Core claims and evidence strength.
4. Reconstructed story.
5. What is useful for the user's research, what is solid, what is weak, and what
   is missing.
6. Follow-up questions, papers, or experiments to verify before trusting or
   building on the paper.

Write the final artifact as a compact version of the paper's argument: introduce
the problem, define needed concepts, explain the method, connect claims to
evidence, and surface limitations in a coherent narrative. Do not output a set
of disconnected reading notes unless the user explicitly asks for notes. Keep
the response concise. Include source locations for important claims.

### Standalone HTML Artifact Requirements

When asked to generate an HTML artifact, article, or similar standalone
deliverable, include the default evidence-grounded review, but do not let the
method section become a short abstract. The method section should usually be one
of the longest sections. A reader should come away understanding how the paper
works and why its claims are or are not justified without returning to the PDF.

The method section must cover:

- the input/output contract of the method
- the key components, modules, variables, or mathematical objects
- the step-by-step procedure or algorithmic flow
- training, inference, optimization, data construction, or proof flow as relevant
- how the proposed method differs from baselines or prior work
- assumptions and dependencies required for the method to work
- enough implementation or reproduction detail to expose what is specified and
  what is missing

Prefer diagrams, tables, pseudocode, or numbered flows in the artifact when they
make the method easier to understand. Preserve source locations for important
method claims.

### Short Blog Rewrite

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

## Edge Cases

- If only a title or abstract is available, label the result as abstract-only and
  avoid claims about experiments or proofs not present in the text.
- If the user asks for a brief artifact, still preserve the main caveat and the
  evidence strength of the central claim.
- If the paper's core claim is unsupported by its experiments, say so directly.
- If the paper is outside the model's current knowledge, rely on the provided
  text or verified sources rather than memory.
