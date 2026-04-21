# Project: debate Skill

This folder maintains a Codex/Claude skill for adversarial debate.

The skill takes a statement, decision, hypothesis, design choice, or plan and evaluates it through three roles:

1. An Affirmative agent argues the strongest honest case for it.
2. A Negative agent argues the strongest honest case against it.
3. A Synthesizer critically weighs both views and produces the final judgment.

Hard constraints:

- Keep all agents concise.
- Require honest debate: no strawmen, invented facts, hidden uncertainty, or knowingly weak arguments.
- Require fact checking for uncertain, current, niche, or high-stakes claims.
- Separate facts, assumptions, inferences, and value judgments.
- Follow host-agent rules for subagent delegation. If delegation is not explicitly authorized, ask for permission or run the roles locally.

## WorkItems

1. Maintain `SKILL.md` as the primary skill content for Codex and Claude.
2. Maintain `scripts/sync-skill.sh` to install the skill.
3. Keep `agents/openai.yaml` aligned with `SKILL.md`.

## Validation

After changing skill metadata or instructions, run:

```bash
python /Users/weaverzhu/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

After changing the sync script, run:

```bash
bash -n scripts/sync-skill.sh
```
