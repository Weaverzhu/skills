#!/usr/bin/env python3
"""Generate a standalone HTML review of one day of Codex CLI usage."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from html import escape
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover - Python < 3.9 fallback
    ZoneInfo = None  # type: ignore[assignment]


TOKEN_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)

CATEGORY_PATTERNS = [
    {
        "name": "Skill creation and maintenance",
        "suggestion": "Create or refine a Codex skill for repeatable workflows",
        "keywords": [
            "skill",
            "skill.md",
            "codex skill",
            "generate a skill",
            "create a skill",
            "$skill",
        ],
    },
    {
        "name": "Paper reading and evidence extraction",
        "suggestion": "Build a paper-reading workflow for claims, methods, labels, and evaluation notes",
        "keywords": [
            "paper",
            "arxiv",
            "according to the paper",
            "citation",
            "literature",
            "ground truth",
            "evaluate",
            "reproduc",
        ],
    },
    {
        "name": "Codebase exploration",
        "suggestion": "Create a codebase explainer that maps files, flows, APIs, and design decisions",
        "keywords": [
            "explain this codebase",
            "explain the codebase",
            "how does this work",
            "walk me through",
            "architecture",
            "codebase",
        ],
    },
    {
        "name": "Implementation and bug fixing",
        "suggestion": "Create a focused implementation workflow with edit, test, and verification steps",
        "keywords": [
            "implement",
            "fix",
            "bug",
            "error",
            "failing",
            "test",
            "add ",
            "update ",
            "refactor",
        ],
    },
    {
        "name": "HTML reports and visualization",
        "suggestion": "Create a report-generation skill with reusable HTML, table, and chart patterns",
        "keywords": [
            "html",
            "artifact",
            "report",
            "dashboard",
            "plot",
            "graph",
            "visualization",
            "timeline",
        ],
    },
    {
        "name": "Automation and local tooling",
        "suggestion": "Create a local automation skill for scripts, CLI commands, and repeatable checks",
        "keywords": [
            "script",
            "cli",
            "command",
            "automation",
            "tool",
            "download",
            "generate",
        ],
    },
    {
        "name": "Review and critique",
        "suggestion": "Create a review skill that standardizes findings, risks, and missing tests",
        "keywords": [
            "review",
            "critique",
            "audit",
            "red team",
            "evaluate",
            "check",
        ],
    },
    {
        "name": "Writing and summarization",
        "suggestion": "Create a writing assistant skill for summaries, drafts, revisions, and structured notes",
        "keywords": [
            "summarize",
            "summary",
            "write",
            "draft",
            "revise",
            "polish",
            "notes",
        ],
    },
]

ACTION_WORDS = (
    "add",
    "build",
    "create",
    "debug",
    "fix",
    "generate",
    "implement",
    "install",
    "review",
    "run",
    "test",
    "update",
    "write",
)


@dataclass
class HistoryEntry:
    session_id: str
    text: str
    ts: datetime | None


@dataclass
class SessionRecord:
    session_id: str
    path: Path
    start_utc: datetime | None = None
    end_utc: datetime | None = None
    cwd: str = ""
    cli_version: str = ""
    source: str = ""
    model_provider: str = ""
    model: str = ""
    effort: str = ""
    title: str = ""
    user_messages: list[str] = field(default_factory=list)
    assistant_messages: list[str] = field(default_factory=list)
    token_usage: dict[str, int] = field(default_factory=dict)
    model_context_window: int | None = None
    tool_calls: Counter[str] = field(default_factory=Counter)
    diagnostics: list[str] = field(default_factory=list)
    lane: int = 0

    @property
    def total_tokens(self) -> int:
        return int(self.token_usage.get("total_tokens") or 0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a standalone HTML report for one day of Codex CLI sessions."
    )
    parser.add_argument(
        "--date",
        help="Local date to review as YYYY-MM-DD. Defaults to today in --timezone.",
    )
    parser.add_argument(
        "--timezone",
        help="IANA timezone such as Asia/Shanghai. Defaults to the system local timezone.",
    )
    parser.add_argument(
        "--codex-home",
        default=os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"),
        help="Codex home directory. Defaults to $CODEX_HOME or ~/.codex.",
    )
    parser.add_argument(
        "--output",
        help="Output HTML path. Defaults to ./codex-day-review-YYYY-MM-DD.html.",
    )
    parser.add_argument(
        "--skill-lookback-days",
        type=int,
        default=14,
        help="History lookback window for skill-candidate frequency hints.",
    )
    return parser.parse_args()


def local_timezone(name: str | None) -> timezone:
    if name:
        if ZoneInfo is None:
            raise SystemExit("Named timezones require Python 3.9+ zoneinfo support.")
        try:
            return ZoneInfo(name)  # type: ignore[return-value]
        except Exception as exc:
            raise SystemExit(f"Could not load timezone {name!r}: {exc}") from exc
    return datetime.now().astimezone().tzinfo or timezone.utc


def parse_iso_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_history_ts(value: Any) -> datetime | None:
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except Exception:
        return None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                items.append(json.loads(stripped))
            except json.JSONDecodeError:
                sys.stderr.write(f"Skipping malformed JSON in {path}:{line_no}\n")
    return items


def load_history(codex_home: Path) -> tuple[dict[str, str], list[HistoryEntry]]:
    path = codex_home / "history.jsonl"
    title_by_session: dict[str, str] = {}
    entries: list[HistoryEntry] = []
    if not path.exists():
        return title_by_session, entries
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, 1):
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                sys.stderr.write(f"Skipping malformed history JSON in {path}:{line_no}\n")
                continue
            session_id = str(item.get("session_id") or "")
            text = normalize_space(str(item.get("text") or ""))
            if not session_id or not text:
                continue
            entries.append(HistoryEntry(session_id, text, parse_history_ts(item.get("ts"))))
            title_by_session.setdefault(session_id, text)
    return title_by_session, entries


def candidate_session_files(codex_home: Path, target: date) -> list[Path]:
    sessions_dir = codex_home / "sessions"
    seen: set[Path] = set()
    files: list[Path] = []
    for offset in (-1, 0, 1):
        selected = target + timedelta(days=offset)
        day_dir = sessions_dir / f"{selected.year:04d}" / f"{selected.month:02d}" / f"{selected.day:02d}"
        if not day_dir.exists():
            continue
        for path in sorted(day_dir.glob("rollout-*.jsonl")):
            if path not in seen:
                files.append(path)
                seen.add(path)
    return files


def extract_session_id(path: Path) -> str:
    match = re.search(r"rollout-[^-]+-[0-9T]+-([0-9a-f-]{36})\.jsonl$", path.name)
    if match:
        return match.group(1)
    fallback = re.search(r"([0-9a-f]{8}-[0-9a-f-]{27})", path.name)
    return fallback.group(1) if fallback else path.stem


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
            continue
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if isinstance(text, str):
            parts.append(text)
    return normalize_space(" ".join(parts))


def clean_prompt(text: str) -> str:
    text = normalize_space(text)
    if text.startswith("<environment_context>"):
        return ""
    if text.startswith("# AGENTS.md instructions"):
        return ""
    return text


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.strip()
        if not key or key in seen:
            continue
        result.append(item)
        seen.add(key)
    return result


def short_text(text: str, limit: int = 110) -> str:
    text = normalize_space(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def parse_session_file(path: Path, history_titles: dict[str, str]) -> SessionRecord:
    record = SessionRecord(session_id=extract_session_id(path), path=path)
    timestamps: list[datetime] = []
    response_user_candidates: list[str] = []

    for item in read_jsonl(path):
        top_ts = parse_iso_timestamp(item.get("timestamp"))
        if top_ts is not None:
            timestamps.append(top_ts)
        kind = item.get("type")
        payload = item.get("payload") or {}
        if not isinstance(payload, dict):
            payload = {}

        if kind == "session_meta":
            record.session_id = str(payload.get("id") or record.session_id)
            meta_ts = parse_iso_timestamp(payload.get("timestamp"))
            if meta_ts is not None:
                record.start_utc = meta_ts
                timestamps.append(meta_ts)
            record.cwd = str(payload.get("cwd") or record.cwd)
            record.cli_version = str(payload.get("cli_version") or record.cli_version)
            record.source = str(payload.get("source") or record.source)
            record.model_provider = str(payload.get("model_provider") or record.model_provider)

        elif kind == "turn_context":
            record.cwd = str(payload.get("cwd") or record.cwd)
            record.model = str(payload.get("model") or record.model)
            record.effort = str(payload.get("effort") or record.effort)

        elif kind == "event_msg":
            event_type = payload.get("type")
            if event_type == "user_message":
                message = clean_prompt(str(payload.get("message") or ""))
                if message:
                    record.user_messages.append(message)
            elif event_type == "token_count":
                info = payload.get("info")
                if isinstance(info, dict):
                    usage = info.get("total_token_usage")
                    if isinstance(usage, dict):
                        record.token_usage = {
                            key: int(usage.get(key) or 0) for key in TOKEN_KEYS
                        }
                    window = info.get("model_context_window")
                    if isinstance(window, int):
                        record.model_context_window = window

        elif kind == "response_item":
            ptype = payload.get("type")
            if ptype == "function_call":
                name = str(payload.get("name") or "tool")
                record.tool_calls[name] += 1
            elif ptype == "message":
                role = payload.get("role")
                text = text_from_content(payload.get("content"))
                if role == "assistant" and text:
                    record.assistant_messages.append(text)
                elif role == "user":
                    prompt = clean_prompt(text)
                    if prompt:
                        response_user_candidates.append(prompt)

    if timestamps:
        record.start_utc = record.start_utc or min(timestamps)
        record.end_utc = max(timestamps)
    if record.start_utc and record.end_utc and record.end_utc < record.start_utc:
        record.end_utc = record.start_utc

    if not record.user_messages:
        record.user_messages = response_user_candidates
    record.user_messages = dedupe_preserve_order(record.user_messages)

    record.title = short_text(
        history_titles.get(record.session_id)
        or (record.user_messages[0] if record.user_messages else "")
        or path.stem,
        120,
    )
    if not record.token_usage:
        record.token_usage = {key: 0 for key in TOKEN_KEYS}
    return record


def overlaps_day(record: SessionRecord, start_utc: datetime, end_utc: datetime) -> bool:
    if record.start_utc is None:
        return False
    end = record.end_utc or record.start_utc
    return record.start_utc < end_utc and end >= start_utc


def clip_interval(
    record: SessionRecord, day_start: datetime, day_end: datetime, tz: timezone
) -> tuple[datetime, datetime]:
    start = (record.start_utc or day_start.astimezone(timezone.utc)).astimezone(tz)
    end = (record.end_utc or record.start_utc or day_start.astimezone(timezone.utc)).astimezone(tz)
    clipped_start = max(start, day_start)
    clipped_end = min(max(end, clipped_start), day_end)
    return clipped_start, clipped_end


def assign_lanes(records: list[SessionRecord], intervals: dict[str, tuple[datetime, datetime]]) -> int:
    lane_ends: list[datetime] = []
    for record in sorted(records, key=lambda item: intervals[item.session_id][0]):
        start, end = intervals[record.session_id]
        for lane, lane_end in enumerate(lane_ends):
            if start >= lane_end:
                record.lane = lane
                lane_ends[lane] = max(end, start + timedelta(minutes=1))
                break
        else:
            record.lane = len(lane_ends)
            lane_ends.append(max(end, start + timedelta(minutes=1)))
    return max(1, len(lane_ends))


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%H:%M:%S")


def format_duration(delta: timedelta) -> str:
    seconds = max(0, int(delta.total_seconds()))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def fmt_int(value: int | float | None) -> str:
    try:
        return f"{int(value or 0):,}"
    except Exception:
        return "0"


def union_duration(intervals: list[tuple[datetime, datetime]]) -> timedelta:
    if not intervals:
        return timedelta()
    ordered = sorted((start, max(end, start)) for start, end in intervals)
    merged: list[tuple[datetime, datetime]] = []
    for start, end in ordered:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return sum((end - start for start, end in merged), timedelta())


def peak_concurrency(intervals: list[tuple[datetime, datetime]]) -> int:
    events: list[tuple[datetime, int]] = []
    for start, end in intervals:
        adjusted_end = max(end, start + timedelta(seconds=1))
        events.append((start, 1))
        events.append((adjusted_end, -1))
    active = 0
    peak = 0
    for _, delta in sorted(events, key=lambda item: (item[0], item[1])):
        active += delta
        peak = max(peak, active)
    return peak


def busiest_hour(records: list[SessionRecord], tz: timezone) -> str:
    starts = Counter()
    for record in records:
        if record.start_utc:
            starts[record.start_utc.astimezone(tz).strftime("%H:00")] += 1
    if not starts:
        return "No session starts"
    hour, count = starts.most_common(1)[0]
    return f"{hour} ({count} start{'s' if count != 1 else ''})"


def top_workdirs(records: list[SessionRecord], limit: int = 4) -> list[tuple[str, int]]:
    counts = Counter(record.cwd or "(unknown)" for record in records)
    return counts.most_common(limit)


def messages_for_day(
    records: list[SessionRecord], history: list[HistoryEntry], target: date, tz: timezone
) -> list[str]:
    messages = [message for record in records for message in record.user_messages]
    if messages:
        return messages
    fallback: list[str] = []
    for entry in history:
        if entry.ts and entry.ts.astimezone(tz).date() == target:
            fallback.append(entry.text)
    return fallback


def history_messages_in_window(
    history: list[HistoryEntry], target: date, tz: timezone, days: int
) -> list[str]:
    if days <= 0:
        return []
    start = target - timedelta(days=days - 1)
    result: list[str] = []
    for entry in history:
        if entry.ts is None:
            continue
        local_date = entry.ts.astimezone(tz).date()
        if start <= local_date <= target:
            result.append(entry.text)
    return result


def category_counts(messages: list[str]) -> tuple[Counter[str], dict[str, list[str]]]:
    counts: Counter[str] = Counter()
    examples: dict[str, list[str]] = defaultdict(list)
    for message in messages:
        lowered = message.lower()
        for category in CATEGORY_PATTERNS:
            if any(keyword in lowered for keyword in category["keywords"]):
                name = category["name"]
                counts[name] += 1
                if len(examples[name]) < 3:
                    examples[name].append(short_text(message, 96))
    return counts, examples


def skill_candidates(
    day_messages: list[str], lookback_messages: list[str]
) -> list[dict[str, Any]]:
    day_counts, day_examples = category_counts(day_messages)
    lookback_counts, lookback_examples = category_counts(lookback_messages)
    candidates: list[dict[str, Any]] = []
    for category in CATEGORY_PATTERNS:
        name = category["name"]
        day_count = day_counts.get(name, 0)
        lookback_count = lookback_counts.get(name, 0)
        if day_count == 0 and lookback_count == 0:
            continue
        strength = "Strong" if day_count >= 2 or lookback_count >= 3 else "Watch"
        examples = day_examples.get(name) or lookback_examples.get(name) or []
        candidates.append(
            {
                "name": name,
                "day_count": day_count,
                "lookback_count": lookback_count,
                "strength": strength,
                "suggestion": category["suggestion"],
                "examples": examples,
            }
        )
    return sorted(
        candidates,
        key=lambda item: (item["strength"] != "Strong", -item["day_count"], -item["lookback_count"], item["name"]),
    )


def is_task_like(message: str) -> bool:
    lowered = message.lower().strip()
    if not lowered:
        return False
    if any(lowered.startswith(word + " ") for word in ACTION_WORDS):
        return True
    return any(f" {word} " in f" {lowered} " for word in ACTION_WORDS)


def tomorrow_tasks(records: list[SessionRecord]) -> list[str]:
    tasks: list[str] = []
    seen: set[str] = set()
    for record in sorted(records, key=lambda item: item.end_utc or item.start_utc or datetime.min.replace(tzinfo=timezone.utc), reverse=True):
        prompt = record.user_messages[-1] if record.user_messages else record.title
        final = record.assistant_messages[-1] if record.assistant_messages else ""
        suggestion = ""
        lowered_final = final.lower()
        if any(marker in lowered_final for marker in ("unable", "not able", "couldn't", "could not", "remaining", "follow up")):
            suggestion = f"Resolve the incomplete follow-up from: {record.title}"
        elif is_task_like(prompt):
            suggestion = f"Validate and continue: {short_text(prompt, 120)}"
        elif "paper" in prompt.lower() or "research" in prompt.lower():
            suggestion = f"Consolidate reading notes from: {record.title}"
        elif record.user_messages:
            suggestion = f"Revisit outcomes from: {record.title}"
        normalized = suggestion.lower()
        if suggestion and normalized not in seen:
            tasks.append(suggestion)
            seen.add(normalized)
        if len(tasks) >= 8:
            break
    if not tasks:
        tasks.append("No obvious unfinished tasks were detected from the available prompts.")
    return tasks


def build_session_rows(
    records: list[SessionRecord],
    intervals: dict[str, tuple[datetime, datetime]],
    tz: timezone,
) -> str:
    rows: list[str] = []
    for index, record in enumerate(sorted(records, key=lambda item: intervals[item.session_id][0]), 1):
        start = (record.start_utc or intervals[record.session_id][0]).astimezone(tz)
        end = (record.end_utc or record.start_utc or intervals[record.session_id][1]).astimezone(tz)
        duration = format_duration(max(end - start, timedelta()))
        tool_summary = ", ".join(f"{name} x{count}" for name, count in record.tool_calls.most_common(3)) or "-"
        rows.append(
            "<tr>"
            f"<td>{index}</td>"
            f"<td><code>{escape(record.session_id[:8])}</code></td>"
            f"<td>{escape(format_datetime(start))} - {escape(format_datetime(end))}</td>"
            f"<td>{escape(duration)}</td>"
            f"<td>{escape(record.title)}</td>"
            f"<td class=\"num\">{fmt_int(record.token_usage.get('total_tokens'))}</td>"
            f"<td class=\"num\">{fmt_int(record.token_usage.get('input_tokens'))}</td>"
            f"<td class=\"num\">{fmt_int(record.token_usage.get('cached_input_tokens'))}</td>"
            f"<td class=\"num\">{fmt_int(record.token_usage.get('output_tokens'))}</td>"
            f"<td>{escape(record.model or '-')}</td>"
            f"<td>{escape(record.effort or '-')}</td>"
            f"<td>{len(record.user_messages)}</td>"
            f"<td>{escape(tool_summary)}</td>"
            f"<td title=\"{escape(record.cwd)}\">{escape(short_text(record.cwd or '-', 48))}</td>"
            "</tr>"
        )
    return "\n".join(rows) or '<tr><td colspan="14">No sessions found for this date.</td></tr>'


def build_skill_rows(candidates: list[dict[str, Any]], lookback_days: int) -> str:
    if not candidates:
        return (
            '<tr><td colspan="6">No repeated task patterns were detected in the selected window.</td></tr>'
        )
    rows: list[str] = []
    for item in candidates:
        examples = "<br>".join(escape(example) for example in item["examples"]) or "-"
        rows.append(
            "<tr>"
            f"<td><span class=\"badge {escape(item['strength'].lower())}\">{escape(item['strength'])}</span></td>"
            f"<td>{escape(item['name'])}</td>"
            f"<td class=\"num\">{fmt_int(item['day_count'])}</td>"
            f"<td class=\"num\">{fmt_int(item['lookback_count'])}</td>"
            f"<td>{escape(item['suggestion'])}</td>"
            f"<td>{examples}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def build_task_list(tasks: list[str]) -> str:
    return "\n".join(f"<li>{escape(task)}</li>" for task in tasks)


def build_workdir_list(records: list[SessionRecord]) -> str:
    items = top_workdirs(records)
    if not items:
        return "<li>No working directories found.</li>"
    return "\n".join(f"<li><code>{escape(path)}</code> <span>{count} session{'s' if count != 1 else ''}</span></li>" for path, count in items)


def session_graph_data(
    records: list[SessionRecord],
    intervals: dict[str, tuple[datetime, datetime]],
    tz: timezone,
) -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = []
    for record in records:
        clipped_start, clipped_end = intervals[record.session_id]
        visual_end = max(clipped_end, clipped_start + timedelta(minutes=1))
        data.append(
            {
                "id": record.session_id,
                "shortId": record.session_id[:8],
                "title": record.title,
                "start": int(clipped_start.timestamp() * 1000),
                "end": int(visual_end.timestamp() * 1000),
                "realEnd": int(clipped_end.timestamp() * 1000),
                "lane": record.lane,
                "tokens": record.total_tokens,
                "turns": len(record.user_messages),
                "timeRange": f"{format_datetime((record.start_utc or clipped_start).astimezone(tz))} - {format_datetime((record.end_utc or record.start_utc or clipped_end).astimezone(tz))}",
            }
        )
    return data


def build_usage_summary(
    records: list[SessionRecord],
    intervals: list[tuple[datetime, datetime]],
    target: date,
    tz: timezone,
) -> list[str]:
    total_tokens = sum(record.total_tokens for record in records)
    total_turns = sum(len(record.user_messages) for record in records)
    total_tool_calls = sum(sum(record.tool_calls.values()) for record in records)
    summed = sum((max(end - start, timedelta()) for start, end in intervals), timedelta())
    distinct = union_duration(intervals)
    peak = peak_concurrency(intervals)
    if not records:
        return [f"No Codex CLI sessions were found for {target.isoformat()} in the configured Codex home."]
    return [
        f"{len(records)} session{'s' if len(records) != 1 else ''} touched {target.isoformat()} with {format_duration(distinct)} of distinct active coverage and {format_duration(summed)} of summed session time.",
        f"Observed token usage totals {fmt_int(total_tokens)} tokens across {total_turns} user turn{'s' if total_turns != 1 else ''}.",
        f"Peak overlap was {peak} concurrent session{'s' if peak != 1 else ''}; busiest start hour was {busiest_hour(records, tz)}.",
        f"Tool activity included {fmt_int(total_tool_calls)} function call{'s' if total_tool_calls != 1 else ''}.",
    ]


def safe_json_for_html(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def render_html(report: dict[str, Any]) -> str:
    html = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Codex Day Review - __DATE__</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #111827;
      --muted: #64748b;
      --line: #d7dde8;
      --blue: #2563eb;
      --green: #16a34a;
      --amber: #d97706;
      --red: #dc2626;
      --violet: #7c3aed;
      --shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    header {
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }
    h1, h2, h3 { margin: 0; letter-spacing: 0; }
    h1 { font-size: 28px; line-height: 1.15; }
    h2 { font-size: 18px; margin-bottom: 12px; }
    h3 { font-size: 14px; color: var(--muted); font-weight: 600; margin-bottom: 6px; }
    main { padding: 22px 32px 40px; max-width: 1500px; margin: 0 auto; }
    .subtle { color: var(--muted); margin-top: 6px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(160px, 1fr));
      gap: 12px;
      margin: 18px 0;
    }
    .metric, section {
      background: var(--panel);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      border-radius: 8px;
    }
    .metric { padding: 14px 16px; }
    .metric strong { display: block; font-size: 24px; line-height: 1.2; }
    section { padding: 18px; margin: 16px 0; }
    .summary-list, .task-list, .workdir-list { margin: 0; padding-left: 20px; }
    .summary-list li, .task-list li, .workdir-list li { margin: 5px 0; }
    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }
    .buttons { display: flex; gap: 8px; flex-wrap: wrap; }
    button {
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      min-height: 32px;
      border-radius: 6px;
      padding: 5px 10px;
      font: inherit;
      cursor: pointer;
    }
    button:hover { border-color: var(--blue); color: var(--blue); }
    #timeline {
      width: 100%;
      min-height: 280px;
      height: __CHART_HEIGHT__px;
      border: 1px solid var(--line);
      background: #fbfcff;
      border-radius: 6px;
      user-select: none;
      touch-action: none;
    }
    .hint { color: var(--muted); font-size: 12px; margin-top: 8px; }
    .table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }
    table { border-collapse: collapse; width: 100%; min-width: 980px; background: #fff; }
    th, td { border-bottom: 1px solid var(--line); padding: 8px 10px; text-align: left; vertical-align: top; }
    th { position: sticky; top: 0; background: #f8fafc; color: #334155; font-size: 12px; white-space: nowrap; }
    td { font-size: 13px; }
    td.num { text-align: right; font-variant-numeric: tabular-nums; }
    code {
      background: #f1f5f9;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      padding: 1px 4px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      padding: 1px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
    }
    .badge.strong { color: #065f46; background: #d1fae5; }
    .badge.watch { color: #92400e; background: #fef3c7; }
    .tooltip {
      position: fixed;
      z-index: 10;
      pointer-events: none;
      max-width: 360px;
      padding: 9px 10px;
      border-radius: 6px;
      background: #111827;
      color: #fff;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.25);
      font-size: 12px;
      display: none;
    }
    @media (max-width: 900px) {
      header { padding: 22px 18px 14px; }
      main { padding: 16px 18px 28px; }
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  </style>
</head>
<body>
  <header>
    <h1>Codex Day Review</h1>
    <div class="subtle">__DATE__ · __TIMEZONE__ · generated __GENERATED_AT__</div>
  </header>
  <main>
    <div class="grid">
      <div class="metric"><h3>Sessions</h3><strong>__SESSION_COUNT__</strong></div>
      <div class="metric"><h3>Total Tokens</h3><strong>__TOTAL_TOKENS__</strong></div>
      <div class="metric"><h3>Distinct Active Time</h3><strong>__ACTIVE_TIME__</strong></div>
      <div class="metric"><h3>Peak Overlap</h3><strong>__PEAK_OVERLAP__</strong></div>
    </div>

    <section>
      <div class="toolbar">
        <h2>Session Timeline</h2>
        <div class="buttons">
          <button id="zoomOut" type="button">Zoom out</button>
          <button id="resetZoom" type="button">Full day</button>
        </div>
      </div>
      <svg id="timeline" role="img" aria-label="Session time ranges"></svg>
      <div class="hint">Drag across the timeline to zoom into a time range. Use the mouse wheel over the chart for centered zoom.</div>
    </section>

    <section>
      <h2>Usage Summary</h2>
      <ul class="summary-list">__SUMMARY_ITEMS__</ul>
      <h3>Top working directories</h3>
      <ul class="workdir-list">__WORKDIR_ITEMS__</ul>
    </section>

    <section>
      <h2>Session Table</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th><th>ID</th><th>Time Range</th><th>Duration</th><th>Title</th>
              <th>Total</th><th>Input</th><th>Cached</th><th>Output</th>
              <th>Model</th><th>Effort</th><th>Turns</th><th>Top Tools</th><th>CWD</th>
            </tr>
          </thead>
          <tbody>__SESSION_ROWS__</tbody>
        </table>
      </div>
    </section>

    <section>
      <h2>Leftover Tasks For Tomorrow</h2>
      <ul class="task-list">__TASK_ITEMS__</ul>
    </section>

    <section>
      <h2>High-Frequency Skill Candidates</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Signal</th><th>Task Pattern</th><th>Day</th><th>Lookback</th><th>Skill Direction</th><th>Examples</th>
            </tr>
          </thead>
          <tbody>__SKILL_ROWS__</tbody>
        </table>
      </div>
      <div class="hint">Lookback uses the previous __LOOKBACK_DAYS__ day(s), including the selected date, from <code>history.jsonl</code>.</div>
    </section>
  </main>
  <div id="tooltip" class="tooltip"></div>
  <script id="report-data" type="application/json">__GRAPH_DATA__</script>
  <script>
    const report = JSON.parse(document.getElementById('report-data').textContent);
    const svg = document.getElementById('timeline');
    const tooltip = document.getElementById('tooltip');
    const colors = ['#2563eb', '#16a34a', '#d97706', '#7c3aed', '#dc2626', '#0891b2', '#4f46e5'];
    let domain = [report.dayStart, report.dayEnd];
    const fullDomain = [report.dayStart, report.dayEnd];
    let dragStart = null;
    let dragRect = null;

    function fmtTime(ms) {
      return new Date(ms).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function render() {
      const width = Math.max(720, svg.clientWidth || 720);
      const laneCount = Math.max(1, report.laneCount);
      const height = Math.max(260, 72 + laneCount * 34);
      svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
      while (svg.firstChild) svg.removeChild(svg.firstChild);

      const left = 78;
      const right = 24;
      const top = 34;
      const axisY = height - 34;
      const plotWidth = width - left - right;
      const laneHeight = 30;
      const span = Math.max(1, domain[1] - domain[0]);
      const x = (ms) => left + ((ms - domain[0]) / span) * plotWidth;
      const msFromX = (px) => domain[0] + ((px - left) / plotWidth) * span;

      const bg = rect(left, top - 8, plotWidth, axisY - top + 8, '#ffffff', '#d7dde8');
      svg.appendChild(bg);

      const tickCount = Math.max(3, Math.min(10, Math.floor(plotWidth / 120)));
      for (let i = 0; i <= tickCount; i++) {
        const ms = domain[0] + (span * i) / tickCount;
        const px = x(ms);
        svg.appendChild(line(px, top - 8, px, axisY, '#e2e8f0'));
        svg.appendChild(text(px, axisY + 19, fmtTime(ms), 'middle', '#475569', 12));
      }

      for (let lane = 0; lane < laneCount; lane++) {
        const y = top + lane * laneHeight;
        svg.appendChild(line(left, y + laneHeight - 4, width - right, y + laneHeight - 4, '#edf2f7'));
        svg.appendChild(text(left - 10, y + 18, `L${lane + 1}`, 'end', '#64748b', 11));
      }

      report.sessions.forEach((session, index) => {
        if (session.end < domain[0] || session.start > domain[1]) return;
        const start = clamp(x(session.start), left, width - right);
        const end = clamp(x(session.end), left, width - right);
        const barWidth = Math.max(3, end - start);
        const y = top + session.lane * laneHeight + 5;
        const bar = rect(start, y, barWidth, 18, colors[index % colors.length], 'none', 5);
        bar.setAttribute('opacity', '0.88');
        bar.dataset.tooltip = `${session.timeRange}\n${session.title}\n${session.tokens.toLocaleString()} tokens · ${session.turns} user turns`;
        bar.addEventListener('mousemove', showTooltip);
        bar.addEventListener('mouseleave', hideTooltip);
        svg.appendChild(bar);
        if (barWidth > 90) {
          const label = text(start + 6, y + 13, `${session.shortId} ${session.title}`, 'start', '#ffffff', 11);
          label.setAttribute('pointer-events', 'none');
          svg.appendChild(label);
        }
      });

      svg.onwheel = (event) => {
        event.preventDefault();
        const bounds = svg.getBoundingClientRect();
        const px = clamp(event.clientX - bounds.left, left, width - right);
        const center = msFromX(px);
        const factor = event.deltaY > 0 ? 1.25 : 0.8;
        zoomAround(center, factor);
      };

      svg.onpointerdown = (event) => {
        const bounds = svg.getBoundingClientRect();
        const px = clamp(event.clientX - bounds.left, left, width - right);
        dragStart = px;
        dragRect = rect(px, top - 8, 1, axisY - top + 8, 'rgba(37,99,235,0.18)', '#2563eb');
        svg.appendChild(dragRect);
        svg.setPointerCapture(event.pointerId);
      };

      svg.onpointermove = (event) => {
        if (dragStart === null || !dragRect) return;
        const bounds = svg.getBoundingClientRect();
        const px = clamp(event.clientX - bounds.left, left, width - right);
        const x0 = Math.min(dragStart, px);
        const w = Math.abs(px - dragStart);
        dragRect.setAttribute('x', x0);
        dragRect.setAttribute('width', w);
      };

      svg.onpointerup = (event) => {
        if (dragStart === null) return;
        const bounds = svg.getBoundingClientRect();
        const px = clamp(event.clientX - bounds.left, left, width - right);
        const delta = Math.abs(px - dragStart);
        if (delta > 8) {
          const start = msFromX(Math.min(dragStart, px));
          const end = msFromX(Math.max(dragStart, px));
          setDomain(start, end);
        } else {
          render();
        }
        dragStart = null;
        dragRect = null;
      };
    }

    function setDomain(start, end) {
      const minSpan = 60 * 1000;
      if (end - start < minSpan) {
        const mid = (start + end) / 2;
        start = mid - minSpan / 2;
        end = mid + minSpan / 2;
      }
      start = clamp(start, fullDomain[0], fullDomain[1] - minSpan);
      end = clamp(end, start + minSpan, fullDomain[1]);
      domain = [start, end];
      render();
    }

    function zoomAround(center, factor) {
      const span = domain[1] - domain[0];
      const nextSpan = clamp(span * factor, 60 * 1000, fullDomain[1] - fullDomain[0]);
      const ratio = (center - domain[0]) / span;
      let start = center - nextSpan * ratio;
      let end = start + nextSpan;
      if (start < fullDomain[0]) {
        start = fullDomain[0];
        end = start + nextSpan;
      }
      if (end > fullDomain[1]) {
        end = fullDomain[1];
        start = end - nextSpan;
      }
      domain = [start, end];
      render();
    }

    function rect(x, y, width, height, fill, stroke, radius = 0) {
      const node = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      node.setAttribute('x', x);
      node.setAttribute('y', y);
      node.setAttribute('width', width);
      node.setAttribute('height', height);
      node.setAttribute('fill', fill);
      node.setAttribute('stroke', stroke);
      if (radius) {
        node.setAttribute('rx', radius);
        node.setAttribute('ry', radius);
      }
      return node;
    }

    function line(x1, y1, x2, y2, stroke) {
      const node = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      node.setAttribute('x1', x1);
      node.setAttribute('y1', y1);
      node.setAttribute('x2', x2);
      node.setAttribute('y2', y2);
      node.setAttribute('stroke', stroke);
      return node;
    }

    function text(x, y, value, anchor, fill, size) {
      const node = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      node.setAttribute('x', x);
      node.setAttribute('y', y);
      node.setAttribute('text-anchor', anchor);
      node.setAttribute('fill', fill);
      node.setAttribute('font-size', size);
      node.textContent = value;
      return node;
    }

    function showTooltip(event) {
      tooltip.textContent = event.target.dataset.tooltip || '';
      tooltip.style.display = 'block';
      tooltip.style.left = `${event.clientX + 12}px`;
      tooltip.style.top = `${event.clientY + 12}px`;
    }

    function hideTooltip() {
      tooltip.style.display = 'none';
    }

    document.getElementById('resetZoom').addEventListener('click', () => {
      domain = [...fullDomain];
      render();
    });
    document.getElementById('zoomOut').addEventListener('click', () => {
      zoomAround((domain[0] + domain[1]) / 2, 1.8);
    });
    window.addEventListener('resize', render);
    render();
  </script>
</body>
</html>
"""
    replacements = {
        "__DATE__": escape(report["date"]),
        "__TIMEZONE__": escape(report["timezone"]),
        "__GENERATED_AT__": escape(report["generated_at"]),
        "__SESSION_COUNT__": fmt_int(report["session_count"]),
        "__TOTAL_TOKENS__": fmt_int(report["total_tokens"]),
        "__ACTIVE_TIME__": escape(report["active_time"]),
        "__PEAK_OVERLAP__": fmt_int(report["peak_overlap"]),
        "__CHART_HEIGHT__": str(report["chart_height"]),
        "__SUMMARY_ITEMS__": "\n".join(f"<li>{escape(item)}</li>" for item in report["summary"]),
        "__WORKDIR_ITEMS__": report["workdir_items"],
        "__SESSION_ROWS__": report["session_rows"],
        "__TASK_ITEMS__": report["task_items"],
        "__SKILL_ROWS__": report["skill_rows"],
        "__LOOKBACK_DAYS__": fmt_int(report["lookback_days"]),
        "__GRAPH_DATA__": safe_json_for_html(report["graph"]),
    }
    for marker, value in replacements.items():
        html = html.replace(marker, value)
    return html


def build_report(args: argparse.Namespace) -> tuple[str, Path]:
    tz = local_timezone(args.timezone)
    target = date.fromisoformat(args.date) if args.date else datetime.now(tz).date()
    codex_home = Path(args.codex_home).expanduser()
    output = (
        Path(args.output).expanduser()
        if args.output
        else Path.cwd() / f"codex-day-review-{target.isoformat()}.html"
    )

    day_start = datetime.combine(target, time.min, tzinfo=tz)
    day_end = day_start + timedelta(days=1)
    day_start_utc = day_start.astimezone(timezone.utc)
    day_end_utc = day_end.astimezone(timezone.utc)

    history_titles, history_entries = load_history(codex_home)
    records = [
        parse_session_file(path, history_titles)
        for path in candidate_session_files(codex_home, target)
    ]
    records = [record for record in records if overlaps_day(record, day_start_utc, day_end_utc)]
    records.sort(key=lambda item: item.start_utc or datetime.max.replace(tzinfo=timezone.utc))

    intervals_by_id = {
        record.session_id: clip_interval(record, day_start, day_end, tz) for record in records
    }
    lane_count = assign_lanes(records, intervals_by_id) if records else 1
    clipped_intervals = [intervals_by_id[record.session_id] for record in records]

    day_messages = messages_for_day(records, history_entries, target, tz)
    lookback_messages = history_messages_in_window(
        history_entries, target, tz, args.skill_lookback_days
    )
    candidates = skill_candidates(day_messages, lookback_messages)
    total_tokens = sum(record.total_tokens for record in records)
    active = union_duration(clipped_intervals)
    peak = peak_concurrency(clipped_intervals)

    graph = {
        "dayStart": int(day_start.timestamp() * 1000),
        "dayEnd": int(day_end.timestamp() * 1000),
        "laneCount": lane_count,
        "sessions": session_graph_data(records, intervals_by_id, tz),
    }
    report = {
        "date": target.isoformat(),
        "timezone": str(args.timezone or tz),
        "generated_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),
        "session_count": len(records),
        "total_tokens": total_tokens,
        "active_time": format_duration(active),
        "peak_overlap": peak,
        "chart_height": max(280, 88 + lane_count * 34),
        "summary": build_usage_summary(records, clipped_intervals, target, tz),
        "workdir_items": build_workdir_list(records),
        "session_rows": build_session_rows(records, intervals_by_id, tz),
        "task_items": build_task_list(tomorrow_tasks(records)),
        "skill_rows": build_skill_rows(candidates, args.skill_lookback_days),
        "lookback_days": args.skill_lookback_days,
        "graph": graph,
    }
    return render_html(report), output


def main() -> int:
    args = parse_args()
    html, output = build_report(args)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
