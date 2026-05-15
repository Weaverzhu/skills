#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
SKILL_NAME="$(basename -- "${SKILL_DIR}")"

CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-${CODEX_HOME:-${HOME}/.codex}/skills}"
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-${CLAUDE_HOME:-${HOME}/.claude}/skills}"

usage() {
  cat <<USAGE
Usage: scripts/sync-skill.sh [--codex-only|--claude-only]

Install this skill globally for Codex and Claude Code.

Environment:
  CODEX_SKILLS_DIR   Codex skills directory. Defaults to \${CODEX_HOME:-\$HOME/.codex}/skills
  CLAUDE_SKILLS_DIR  Claude Code skills directory. Defaults to \${CLAUDE_HOME:-\$HOME/.claude}/skills
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

copy_to() {
  local dest_root="$1"
  local dest_dir="${dest_root}/${SKILL_NAME}"

  mkdir -p "${dest_root}"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete \
      --exclude ".git/" \
      --exclude ".DS_Store" \
      --exclude "__pycache__/" \
      "${SKILL_DIR}/" "${dest_dir}/"
  else
    rm -rf "${dest_dir}"
    mkdir -p "${dest_dir}"
    cp -R "${SKILL_DIR}/." "${dest_dir}/"
    find "${dest_dir}" -name ".DS_Store" -delete
    find "${dest_dir}" -type d -name "__pycache__" -prune -exec rm -rf {} +
  fi

  echo "synced ${SKILL_NAME} -> ${dest_dir}"
}

if [[ "${INSTALL_CODEX}" -eq 1 ]]; then
  copy_to "${CODEX_SKILLS_DIR}"
fi

if [[ "${INSTALL_CLAUDE}" -eq 1 ]]; then
  copy_to "${CLAUDE_SKILLS_DIR}"
fi
