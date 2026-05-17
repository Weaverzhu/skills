#!/usr/bin/env python3
"""Summarize raw agent trajectory files for quick harness triage."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


TEXT_SUFFIXES = {".log", ".md", ".txt", ".trace"}
STRUCTURED_SUFFIXES = {".json", ".jsonl", ".ndjson"}


def iter_paths(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in STRUCTURED_SUFFIXES | TEXT_SUFFIXES:
                    files.append(child)
        elif path.is_file():
            files.append(path)
    return sorted(files)


def load_records(path: Path) -> list[Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        records: list[Any] = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                records.append({"_parse_error": f"{path}:{line_no}", "text": line})
        return records
    if suffix == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return [{"_parse_error": f"{path}: {exc}", "text": text}]
        return data if isinstance(data, list) else [data]
    return [{"text": text}]


def walk(value: Any, path: str = "") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield from walk(child, child_path)


def key_name(path: str) -> str:
    cleaned = path.replace("]", "")
    if not cleaned:
        return ""
    return cleaned.split(".")[-1].split("[")[0].lower()


def summarize_record(record: Any) -> dict[str, Any]:
    strings_by_key: Counter[str] = Counter()
    counts: Counter[str] = Counter()
    errors: list[str] = []
    tool_names: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    total_chars = 0
    max_string = ("", 0)

    for path, value in walk(record):
        key = key_name(path)
        if isinstance(value, str):
            length = len(value)
            total_chars += length
            if key:
                strings_by_key[key] += length
            if length > max_string[1]:
                max_string = (path or "<root>", length)
            lowered = value.lower()
            if "error" in key or "exception" in key or "traceback" in lowered:
                errors.append(value[:220].replace("\n", " "))
        elif isinstance(value, list) and key:
            counts[f"{key}_items"] += len(value)
        elif isinstance(value, dict) and key:
            counts[f"{key}_objects"] += 1

        if key in {"role", "speaker"} and isinstance(value, str):
            roles[value] += 1
        if key in {"tool", "tool_name", "name", "function"} and isinstance(value, str):
            parent = path.rsplit(".", 1)[0].lower()
            if "tool" in parent or "call" in parent or key.startswith("tool"):
                tool_names[value] += 1

    return {
        "chars": total_chars,
        "estimated_tokens": round(total_chars / 4),
        "strings_by_key": strings_by_key,
        "counts": counts,
        "errors": errors,
        "tool_names": tool_names,
        "roles": roles,
        "max_string": max_string,
    }


def print_counter(title: str, counter: Counter[str], limit: int) -> None:
    if not counter:
        return
    print(f"\n{title}")
    for key, value in counter.most_common(limit):
        print(f"  {key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Trajectory files or directories")
    parser.add_argument("--top", type=int, default=12, help="Number of top entries to print")
    args = parser.parse_args()

    files = iter_paths(args.paths)
    if not files:
        print("No trajectory-like files found.")
        return 1

    aggregate_strings: Counter[str] = Counter()
    aggregate_counts: Counter[str] = Counter()
    aggregate_tools: Counter[str] = Counter()
    aggregate_roles: Counter[str] = Counter()
    file_chars: Counter[str] = Counter()
    parse_errors: list[str] = []
    trace_errors: list[tuple[str, str]] = []
    record_count = 0
    max_strings: list[tuple[int, str, str]] = []

    for file in files:
        records = load_records(file)
        for record in records:
            record_count += 1
            summary = summarize_record(record)
            chars = int(summary["chars"])
            file_chars[str(file)] += chars
            aggregate_strings.update(summary["strings_by_key"])
            aggregate_counts.update(summary["counts"])
            aggregate_tools.update(summary["tool_names"])
            aggregate_roles.update(summary["roles"])
            max_path, max_len = summary["max_string"]
            if max_len:
                max_strings.append((max_len, str(file), max_path))
            for error in summary["errors"]:
                trace_errors.append((str(file), error))
            if isinstance(record, dict) and "_parse_error" in record:
                parse_errors.append(str(record["_parse_error"]))

    total_chars = sum(file_chars.values())
    print("# Trajectory Summary")
    print(f"Files: {len(files)}")
    print(f"Records: {record_count}")
    print(f"Characters in string fields: {total_chars}")
    print(f"Estimated tokens from strings: {round(total_chars / 4)}")

    print_counter("Largest files by string volume", file_chars, args.top)
    print_counter("String volume by key", aggregate_strings, args.top)
    print_counter("Repeated object/list counts", aggregate_counts, args.top)
    print_counter("Roles", aggregate_roles, args.top)
    print_counter("Tool names", aggregate_tools, args.top)

    if max_strings:
        print("\nLargest individual strings")
        for length, file, path in sorted(max_strings, reverse=True)[: args.top]:
            print(f"  {length} chars  {file}  {path}")

    if parse_errors:
        print("\nParse errors")
        for item in parse_errors[: args.top]:
            print(f"  {item}")

    if trace_errors:
        print("\nError-like fields or tracebacks")
        for file, error in trace_errors[: args.top]:
            print(f"  {file}: {error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
