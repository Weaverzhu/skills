# Paper Reading Skill Workflow

## Goal

Help an LLM read research papers as evidence work, not as generic summarization.
The output should make the paper easier to understand, but it must preserve where
claims come from, how strongly they are supported, and what remains uncertain.

## Hard Constraints

- Start from the user's reading intent: triage, deep understanding, implementation,
  literature comparison, or critical review.
- Ground important statements in paper locations such as section, page, figure,
  table, theorem, algorithm, or appendix.
- Separate author-stated claims from inferred narrative and external judgment.
- Prefer asking for the missing paper, scope, or depth over silently inventing
  context.
- Do not assume every paper is empirical. Theory, system, benchmark, dataset,
  position, survey, and negative-result papers need different evidence checks.
- Keep final outputs concise, but do not compress away caveats, assumptions,
  definitions, or failure modes.

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

Before detailed reading, identify the user's goal and choose depth:

- Triage: decide whether the paper is worth reading.
- Understanding: explain the paper's argument and technical mechanism.
- Implementation: extract reproducible details, algorithms, settings, and missing
  information.
- Literature comparison: position the paper against prior and follow-up work.
- Review critique: evaluate novelty, correctness, evidence, clarity, and risk.

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

### 7. Final Output

Default final structure:

1. Bottom line.
2. Paper card.
3. Core claims and evidence strength.
4. Reconstructed story.
5. What is solid, what is weak, and what is missing.
6. Questions to verify before trusting or building on the paper.

Keep the response concise. Include source locations for important claims.

## Edge Cases

- If only a title or abstract is available, label the result as abstract-only and
  avoid claims about experiments or proofs not present in the text.
- If the user asks for a very short summary, still preserve the main caveat and
  the evidence strength of the central claim.
- If the paper's core claim is unsupported by its experiments, say so directly.
- If the paper is outside the model's current knowledge, rely on the provided
  text or verified sources rather than memory.
