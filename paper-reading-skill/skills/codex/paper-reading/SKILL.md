---
name: paper-reading
description: Use this skill to read, summarize, critique, or extract implementation details from research papers with evidence-grounded claims, source locations, and uncertainty controls. Trigger for requests involving paper triage, deep paper understanding, claim/evidence audits, literature comparison, reproducibility checks, or peer-review-style critique.
---

# Paper Reading

Use this skill to treat a research paper as an argument with evidence, not as text
to summarize generically.

## Hard Constraints

- Start from the user's reading intent: triage, deep understanding,
  implementation, literature comparison, or critical review.
- Ground important statements in source locations: section, page, figure, table,
  theorem, algorithm, or appendix.
- Separate author-stated claims, inferred narrative, and your judgment.
- Ask for the paper, scope, or depth when missing information changes the answer.
- Do not assume every paper is empirical. Adapt evidence checks to paper type.
- Keep outputs concise, but preserve caveats, assumptions, definitions, and
  failure modes.

## Workflow

1. **Establish intent.** Identify whether the user wants triage, understanding,
   implementation, comparison, or critique. Ask one concise question only when
   the intent materially changes the work.
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
   evidence strength, reconstructed story, solid/weak/missing points, and
   verification questions.

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
