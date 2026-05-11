#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CODEX_SRC="$ROOT/skills/codex/paper-reading"
CLAUDE_SRC="$ROOT/skills/claude-code/paper-reading"

CODEX_DEST="${CODEX_HOME:-$HOME/.codex}/skills/paper-reading"
CLAUDE_DEST="${CLAUDE_HOME:-$HOME/.claude}/skills/paper-reading"

copy_skill() {
  local src="$1"
  local dest="$2"
  local label="$3"

  if [[ ! -d "$src" ]]; then
    echo "Missing $label source: $src" >&2
    exit 1
  fi

  mkdir -p "$(dirname "$dest")"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$src/" "$dest/"
  else
    rm -rf "$dest"
    mkdir -p "$dest"
    cp -R "$src/." "$dest/"
  fi

  echo "Synced $label skill to $dest"
}

copy_skill "$CODEX_SRC" "$CODEX_DEST" "Codex"
copy_skill "$CLAUDE_SRC" "$CLAUDE_DEST" "Claude Code"
