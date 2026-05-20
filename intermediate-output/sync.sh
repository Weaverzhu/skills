#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

CODEX_SRC_ROOT="${ROOT}/skills/codex"
CLAUDE_SRC_ROOT="${ROOT}/skills/claude-code"

CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-${CODEX_HOME:-${HOME}/.codex}/skills}"
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-${CLAUDE_HOME:-${HOME}/.claude}/skills}"

usage() {
  cat <<USAGE
Usage: ./sync [--codex-only|--claude-only]

Syncs all skills under this project into global skill folders:
  Codex:       \${CODEX_SKILLS_DIR:-\${CODEX_HOME:-\$HOME/.codex}/skills}
  Claude Code: \${CLAUDE_SKILLS_DIR:-\${CLAUDE_HOME:-\$HOME/.claude}/skills}

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

copy_skill() {
  local src="$1"
  local dest_root="$2"
  local label="$3"
  local name
  name="$(basename -- "${src}")"
  local dest="${dest_root}/${name}"

  if [[ ! -f "${src}/SKILL.md" ]]; then
    echo "error: missing ${label} SKILL.md: ${src}/SKILL.md" >&2
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

  echo "synced ${label} ${name} skill -> ${dest}"
}

sync_tree() {
  local src_root="$1"
  local dest_root="$2"
  local label="$3"

  if [[ ! -d "${src_root}" ]]; then
    echo "error: missing ${label} skills source: ${src_root}" >&2
    exit 1
  fi

  local found=0
  local src
  for src in "${src_root}"/*; do
    if [[ -d "${src}" ]]; then
      found=1
      copy_skill "${src}" "${dest_root}" "${label}"
    fi
  done

  if [[ "${found}" -eq 0 ]]; then
    echo "error: no ${label} skills found under ${src_root}" >&2
    exit 1
  fi
}

if [[ "${INSTALL_CODEX}" -eq 1 ]]; then
  sync_tree "${CODEX_SRC_ROOT}" "${CODEX_SKILLS_DIR}" "Codex"
fi

if [[ "${INSTALL_CLAUDE}" -eq 1 ]]; then
  sync_tree "${CLAUDE_SRC_ROOT}" "${CLAUDE_SKILLS_DIR}" "Claude Code"
fi
