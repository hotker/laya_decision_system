"""
Input Data Source
=================
Supports reading decision data from JSON/CSV/stdin instead of hardcoded values

Usage:
    from data_source import load_data

    # Load from JSON file
    data = load_data("data.json")

    # Load from CSV file (specify text column)
    data = load_data("data.csv", text_column="body")

    # Load from stdin (JSON array)
    data = load_data("-")
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_data(
    source: str | None = None,
    text_column: str = "body",
) -> list[dict[str, Any]] | None:
    """Load input data from data source

    Args:
        source: File path (.json / .csv / "-" for stdin), None means use default data
        text_column: Column name for text in CSV

    Returns:
        [{"body": "..."}, ...] or None (use default data)
    """
    if source is None:
        return None

    source = source.strip()

    if source == "-":
        return _load_stdin(text_column)

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Data file does not exist: {source}")

    ext = path.suffix.lower()
    if ext == ".json":
        return _load_json(path, text_column)
    elif ext in (".csv", ".tsv"):
        return _load_csv(path, text_column, sep="," if ext == ".csv" else "\t")
    else:
        raise ValueError(f"Unsupported data format: {ext} (support .json / .csv / .tsv)")


def _load_stdin(text_column: str) -> list[dict[str, Any]]:
    """Read JSON array from stdin"""
    text = sys.stdin.read().strip()
    if not text:
        return []

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"stdin JSON parsing failed: {exc}")

    return _normalize_data(data, text_column)


def _load_json(path: Path, text_column: str) -> list[dict[str, Any]]:
    """Load from JSON file"""
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON parsing failed: {exc}")

    return _normalize_data(data, text_column)


def _normalize_data(data: Any, text_column: str) -> list[dict[str, Any]]:
    """Uniformly process JSON data, extract body field"""
    if isinstance(data, list):
        return _normalize_list(data, text_column)
    elif isinstance(data, dict):
        # Compatible with output format: {"results": [...]} or {"data": [...]}
        for key in ("results", "data", "items"):
            if key in data and isinstance(data[key], list):
                return _normalize_list(data[key], text_column)
        # Single record
        body = data.get(text_column, data.get("body", data.get("text", "")))
        if body:
            return [{"body": body, **{k: v for k, v in data.items() if k not in (text_column, "body", "text")}}]
        return []
    else:
        raise ValueError("JSON data expects array or object")


def _normalize_list(items: list, text_column: str) -> list[dict[str, Any]]:
    """Extract body from list with safe key access"""
    results: list[dict] = []
    for item in items:
        if isinstance(item, str):
            results.append({"body": item})
        elif isinstance(item, dict):
            # Safely extract body with fallback chain
            body = item.get(text_column) or item.get("body") or item.get("text") or ""
            if body:
                # Preserve extra fields from original item
                extra = {k: v for k, v in item.items() if k not in (text_column, "body", "text")}
                results.append({"body": body, **extra})
    return results


def _load_csv(path: Path, text_column: str, sep: str) -> list[dict[str, Any]]:
    """Load from CSV file"""
    results: list[dict] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=sep)
        for row in reader:
            body = row.get(text_column, row.get("body", ""))
            if body:
                extra = {k: v for k, v in row.items() if k not in (text_column, "body")}
                results.append({"body": body, **extra})
    return results


def save_output(data: list[dict], path: str, fmt: str = "json") -> None:
    """Write processed results to file"""
    out_path = Path(path)

    if fmt == "csv":
        if not data:
            out_path.touch()
            return
        fields = list(data[0].keys())
        with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data)
    elif fmt == "json":
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError(f"Unsupported output format: {fmt}")

    logger.info("output_saved path=%s format=%s count=%d", out_path, fmt, len(data))