"""
Output Utilities
================
Unified handling of decision result saving and statistics

Features:
  - JSON result saving (auto-unique filenames)
  - CSV result saving
  - Unified format for single/batch results
  - Old file auto-cleanup

Usage:
    from output import save_results, list_output_files, clean_old_files
"""

from __future__ import annotations

import csv
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from config.config import get_config

logger = logging.getLogger(__name__)

# ─── Unified Output Format ──────────────────────────────────────

OUTPUT_DIR = get_config().output.directory


def _ensure_dir() -> Path:
    """Ensure output directory exists"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def _gen_filename(prefix: str) -> str:
    """Generate filename with unique identifier to avoid overwriting within same second"""
    _ensure_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:6]
    return str(OUTPUT_DIR / f"{prefix}_{ts}_{uid}.json")


# ─── Saving ─────────────────────────────────────────────────────


def _flatten_value(val: object) -> object:
    """Flatten nested structures for CSV export."""
    if isinstance(val, dict):
        return json.dumps(val, ensure_ascii=False, default=str)
    if isinstance(val, (list, tuple)):
        return json.dumps(val, ensure_ascii=False, default=str)
    return val


def save_results(
    results: list[dict],
    prefix: str = "decision",
    decision_type: str | None = None,
    trace_id: str | None = None,
    fmt: str = "json",
) -> str:
    """Save batch results as unified format

    Format:
    {
      "metadata": { ... },
      "results": [ ... ]
    }

    Args:
        results: Result data list
        prefix: Filename prefix
        decision_type: Category label for metadata
        trace_id: Trace ID for tracking
        fmt: Output format ('json' or 'csv')

    Returns:
        Path to the saved file
    """
    if fmt == "csv":
        return save_results_csv(results, prefix=prefix)

    cfg = get_config()
    path = _gen_filename(f"batch_decision_{prefix}")

    data = {
        "metadata": {
            "system": cfg.system_name,
            "version": cfg.version,
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type or prefix,
            "count": len(results),
            "trace_id": trace_id,
        },
        "results": results,
    }

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("results_saved path=%s count=%d", path, len(results))
        return path
    except OSError as exc:
        logger.error("save_failed path=%s error=%s", path, exc)
        raise


def save_single_result(
    result: dict,
    prefix: str = "decision",
    decision_type: str | None = None,
    trace_id: str | None = None,
    fmt: str = "json",
) -> str:
    """Save single result as unified JSON format"""
    if fmt == "csv":
        return save_results_csv([result], prefix=prefix)

    cfg = get_config()
    path = _gen_filename(prefix)

    data = {
        "metadata": {
            "system": cfg.system_name,
            "version": cfg.version,
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type or prefix,
            "trace_id": trace_id,
        },
        "result": result,
    }

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("single_result_saved path=%s", path)
        return path
    except OSError as exc:
        logger.error("save_single_failed path=%s error=%s", path, exc)
        raise


def save_results_csv(
    results: list[dict],
    prefix: str = "decision",
) -> str:
    """Save batch results as CSV

    Returns CSV file path
    """
    _ensure_dir()
    path = str(OUTPUT_DIR / f"{prefix}_{uuid.uuid4().hex[:6]}.csv")

    if not results:
        logger.warning("save_csv_empty")
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        return path

    # Flatten data with safe key access
    flat: list[dict] = []
    for item in results:
        # Safely extract metadata and answers
        meta = item.get("metadata") or {}
        if "answers" in item:
            answers = item["answers"]
        elif "result" in item:
            answers = {"result": item["result"]}
        else:
            # Fallback: use the whole item as answers
            answers = {"item": item}
        row = {**meta, **answers}
        flat.append(row)

    if not flat:
        logger.warning("save_csv_empty after flattening")
        return path

    # Flatten nested structures for CSV compatibility
    for row in flat:
        for key, val in row.items():
            row[key] = _flatten_value(val)

    fields = list(flat[0].keys())
    try:
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(flat)
        logger.info("csv_saved path=%s rows=%d", path, len(flat))
    except OSError as exc:
        logger.error("save_csv_failed path=%s error=%s", exc)
        raise

    return path


# ─── Query & Cleanup ───────────────────────────────────────────


def list_output_files(pattern: str = "batch_decision_*.json") -> list[Path]:
    """List files in output directory, sorted by modification time descending"""
    _ensure_dir()
    files = list(OUTPUT_DIR.glob(pattern))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files


def clean_old_files(
    pattern: str = "batch_decision_*.json",
    keep_count: int | None = None,
) -> int:
    """Clean old files, keep only latest keep_count

    Returns:
        Number of deleted files
    """
    if keep_count is None:
        keep_count = get_config().output.max_files

    files = list_output_files(pattern)
    deleted = 0
    for f in files[keep_count:]:
        f.unlink()
        deleted += 1
        logger.info("cleaned_old_file path=%s", f.name)
    return deleted


def clean_all(pattern: str = "*.json") -> int:
    """Clear all output files

    Returns:
        Number of deleted files
    """
    _ensure_dir()
    files = list(OUTPUT_DIR.glob(pattern))
    for f in files:
        f.unlink()
    logger.info("all_cleared count=%d", len(files))
    return len(files)