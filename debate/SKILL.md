---
name: debate
description: Run an adaptive-depth adversarial debate over a statement, decision, hypothesis, design choice, or plan by assigning one agent to argue for it, one agent to argue against it, and a final critical synthesis that weighs both views. Use when the user asks for debate, red-team/blue-team analysis, pro/con agent review, adversarial evaluation, or explicitly invokes $debate.
---

# debate

Use this skill to test a statement through disciplined opposition. The goal is not to make both sides sound equally plausible; it is to expose the strongest honest case for each side, check facts, and produce a judgment at the depth the question deserves.

## Hard Constraints

- Spawn subagents only when the user explicitly asks to use this skill, asks for subagents, or the host runtime policy permits delegation. If not, ask for permission or run the roles locally.
- Match detail to the request and stakes. Prefer dense evidence and clear assumptions; expand when brevity would hide material uncertainty, tradeoffs, or evidence quality.
- Do not let an agent invent facts, hide uncertainty, strawman the other side, or argue past known contradictory evidence.
- Use current sources for unstable facts such as laws, prices, APIs, company details, news, schedules, or model/product availability.
- Separate facts, assumptions, value judgments, and inferences.
- If the proposition is ambiguous enough to change the debate outcome, ask one clarifying question before starting.

## Workflow

1. Restate the proposition in one sentence.
2. State scope, hard constraints, decision criteria, and intended depth.
3. Identify facts that must be verified before debate. Verify them first when they are unstable or high-stakes.
4. Run two independent passes at the chosen depth:
   - **Affirmative**: strongest honest case supporting the proposition.
   - **Negative**: strongest honest case opposing the proposition.
5. Synthesize critically:
   - Compare evidence quality, not rhetorical force.
   - Identify hidden assumptions and failure modes.
   - Name what evidence would change the conclusion.
   - Give a final judgment with confidence.

Do not show long hidden reasoning. Share concise conclusions, assumptions, checks, and sources when applicable.

## Depth Policy

Use the user's requested level of detail when stated. Otherwise choose the smallest depth that can honestly evaluate the proposition:

- **Brief**: User asks for quick, short, summary, or tldr. Each side gets 1-2 tight paragraphs or 3-5 bullets. Synthesis is short but still states the decisive uncertainty.
- **Standard**: Default for ordinary claims. Each side gets 2-4 developed arguments with evidence, assumptions, and weaknesses. Synthesis compares argument quality and gives a reasoned judgment.
- **Expanded**: Use when the user asks for detail/deep analysis, or when the proposition is complex, current, high-stakes, quantitative, policy/legal/medical/financial, or depends on contested facts. Each side should get enough room to present evidence, counter-evidence, assumptions, and failure modes separately. Synthesis should explain why one side is stronger, what would change the conclusion, and any residual uncertainty.

Do not compress roles into one paragraph when the debate turns on multiple independent facts or assumptions. Do not add length by repeating claims, padding rhetoric, or treating weak arguments as equal to strong ones.

## Subagent Prompts

Use these templates when delegation is available.

### Affirmative

```text
You are the Affirmative agent in an adaptive-depth adversarial debate.

Proposition: <exact proposition>
Scope and criteria: <scope, constraints, decision criteria>
Depth: <brief | standard | expanded, plus any user-requested output budget>

Task:
- Build the strongest honest case for the proposition.
- Verify factual claims when they are uncertain, current, niche, or high-stakes.
- State key assumptions and the most serious weakness in your case.
- Do not strawman the opposing side or omit known contradictory evidence.
- Match the requested depth: concise when asked, but detailed enough that evidence quality, assumptions, and uncertainty are visible.

Output:
- Position
- Strongest arguments
- Evidence and checks
- Assumptions
- Weakest point
```

### Negative

```text
You are the Negative agent in an adaptive-depth adversarial debate.

Proposition: <exact proposition>
Scope and criteria: <scope, constraints, decision criteria>
Depth: <brief | standard | expanded, plus any user-requested output budget>

Task:
- Build the strongest honest case against the proposition.
- Verify factual claims when they are uncertain, current, niche, or high-stakes.
- State key assumptions and the most serious weakness in your case.
- Do not strawman the supporting side or omit known supporting evidence.
- Match the requested depth: concise when asked, but detailed enough that evidence quality, assumptions, and uncertainty are visible.

Output:
- Position
- Strongest arguments
- Evidence and checks
- Assumptions
- Weakest point
```

### Synthesizer

```text
You are the final Synthesizer for an adaptive-depth adversarial debate.

Proposition: <exact proposition>
Scope and criteria: <scope, constraints, decision criteria>
Depth: <brief | standard | expanded, plus any user-requested output budget>
Affirmative brief: <brief>
Negative brief: <brief>

Task:
- Weigh both briefs critically.
- Prefer verified facts and decision-relevant arguments.
- Flag unsupported claims, hidden assumptions, and missing evidence.
- Explain what would change the conclusion.
- Give a final judgment and confidence level.
- Match the requested depth and make the final judgment proportionate to evidence quality.

Output:
- Bottom line
- Best affirmative points
- Best negative points
- Key uncertainty
- Final judgment
```

## Final Answer Shape

Use this structure unless the user requests another format:

```text
Proposition: ...

Affirmative: ...

Negative: ...

Critical synthesis: ...

Judgment: ... Confidence: low/medium/high.
```

For standard or expanded depth, use bullets under each role rather than one compressed paragraph when there are multiple independent arguments. For high-stakes, current, or source-dependent domains, add a source list and make uncertainty visible.
