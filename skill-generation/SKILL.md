---
name: skill-generation
description: Summarize the current dialog into a reusable Codex or Claude Code skill, choose a topic-related skill folder under /Users/weaverzhu/Documents/workspace/vibe-coding-playground/skills, handle existing-skill conflicts by asking the user, and provide a sync path for installing the skill globally.
---

# skill-generation

Use this skill when the user wants the current conversation, workflow, tool pattern, domain procedure, or repeated implementation approach turned into a reusable local skill.

The output is a skill directory under:

```text
/Users/weaverzhu/Documents/workspace/vibe-coding-playground/skills
```

## Workflow

1. Identify the skill topic from the dialog.
   - Use a concise kebab-case folder name related to the topic, such as `paper-reading`, `keynote-automation`, or `api-migration`.
   - The folder name should be the skill name unless the existing ecosystem clearly uses another convention.
2. Check whether the target folder already exists.
   - If it exists and appears to be a skill, stop and ask the user whether to update it, replace it, or choose a new name.
   - Do not overwrite existing skill files without explicit user direction.
3. Create the minimum useful skill structure:

```text
<skill-name>/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
`-- scripts/
    `-- sync-skill.sh
```

4. Write `SKILL.md`.
   - Include YAML frontmatter with `name` and `description`.
   - Make the description trigger-oriented: say when the skill should be used.
   - Summarize the reusable workflow from the conversation, not the entire transcript.
   - Include only durable instructions, tool choices, constraints, file locations, and validation steps that matter for future use.
   - Keep the body concise. Move large examples, schemas, or detailed references into `references/` only when they are necessary.
5. Write `agents/openai.yaml`.
   - Include `display_name`, `short_description`, and `default_prompt`.
   - Keep values human-facing and consistent with `SKILL.md`.
6. Add `scripts/sync-skill.sh`.
   - It must install the skill into both Codex and Claude Code by default.
   - Default destinations:
     - Codex: `${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>`
     - Claude Code: `${CLAUDE_HOME:-$HOME/.claude}/skills/<skill-name>`
   - Support `--codex-only`, `--claude-only`, and `--help`.
   - Prefer `rsync -a --delete` when available, with a safe fallback to `cp -R`.
7. Validate the result.
   - Confirm `SKILL.md` has valid frontmatter and required fields.
   - Confirm `agents/openai.yaml` exists and matches the skill.
   - Confirm `scripts/sync-skill.sh` is executable and its help text works.

## Conflict Handling

If a target skill folder already exists, ask one concise question before editing:

```text
`<skill-name>` already exists. Should I update it in place, replace it, or create a new skill under a different name?
```

Only continue after the user chooses.

## Skill Quality Bar

- Make the skill procedural enough that a future agent can follow it without the original conversation.
- Do not include private scratch notes, temporary debugging details, or one-off user preferences unless they are central to the skill.
- Prefer deterministic scripts for fragile or repeated install/setup behavior.
- Do not create extra documentation files such as `README.md`, `CHANGELOG.md`, or `INSTALLATION.md` unless the user explicitly asks.
- Keep generated files ASCII unless the destination skill already uses non-ASCII content for a clear reason.
