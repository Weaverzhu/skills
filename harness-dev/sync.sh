#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

SKILL_NAME="harness-dev"
CODEX_SRC="${ROOT}/skills/codex/${SKILL_NAME}"
CLAUDE_SRC="${ROOT}/skills/claude-code/${SKILL_NAME}"

CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-${CODEX_HOME:-${HOME}/.codex}/skills}"
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-${CLAUDE_HOME:-${HOME}/.claude}/skills}"

usage() {
  cat <<USAGE
Usage: ./sync.sh [--codex-only|--claude-only]

Syncs the harness-dev skill into global skill folders:
  Codex:      \${CODEX_SKILLS_DIR:-\${CODEX_HOME:-\$HOME/.codex}/skills}/harness-dev
  Claude Code: \${CLAUDE_SKILLS_DIR:-\${CLAUDE_HOME:-\$HOME/.claude}/skills}/harness-dev

Environment:
  CODEX_SKILLS_DIR   Override Codex skills directory.
  CLAUDE_SKILLS_DIR  Override Claude Code skills directory.
USAGE
}

INSTALL_CODEX=1
INSTALL_CLAUDE=1

case "${1:-}" in
  "")
    ;;
  --codex-only)
    INSTALL_CLAUDE=0
    ;;
  --claude-only)
    INSTALL_CODEX=0
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

if [[ "$#" -gt 1 ]]; then
  usage >&2
  exit 2
fi

copy_to() {
  local src="$1"
  local dest_root="$2"
  local label="$3"
  local dest="${dest_root}/${SKILL_NAME}"

  if [[ ! -d "${src}" ]]; then
    echo "error: missing ${label} source: ${src}" >&2
    exit 1
  fi

  mkdir -p "${dest_root}"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete \
      --exclude ".git/" \
      --exclude ".DS_Store" \
      --exclude "__pycache__/" \
      "${src}/" "${dest}/"
  else
    rm -rf "${dest}"
    mkdir -p "${dest}"
    cp -R "${src}/." "${dest}/"
    find "${dest}" -name ".DS_Store" -delete
    find "${dest}" -type d -name "__pycache__" -prune -exec rm -rf {} +
  fi

  echo "synced ${label} ${SKILL_NAME} skill -> ${dest}"
}

if [[ "${INSTALL_CODEX}" -eq 1 ]]; then
  copy_to "${CODEX_SRC}" "${CODEX_SKILLS_DIR}" "Codex"
fi

if [[ "${INSTALL_CLAUDE}" -eq 1 ]]; then
  copy_to "${CLAUDE_SRC}" "${CLAUDE_SKILLS_DIR}" "Claude Code"
fi
