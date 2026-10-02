"""
输出工具
========
统一处理决策结果的保存和统计

功能：
  - JSON 结果保存（自动去重文件名）
  - CSV 结果保存
  - 单条/批量结果统一格式
  - 旧文件自动清理

使用方式：
    from output import save_results, list_output_files, clean_old_files
"""

from __future__ import annotations

import csv
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from config.config import get_config

logger = logging.getLogger(__name__)

# ─── 统一输出格式 ──────────────────────────────────────────────

OUTPUT_DIR = get_config().output.directory


def _ensure_dir() -> Path:
    """确保输出目录存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def _gen_filename(prefix: str) -> str:
    """生成带唯一标识的文件名，避免同一秒内覆盖"""
    _ensure_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:6]
    return str(OUTPUT_DIR / f"{prefix}_{ts}_{uid}.json")


# ─── 保存 ──────────────────────────────────────────────────────


def save_results(
    results: list[dict],
    prefix: str = "decision",
    decision_type: str | None = None,
    trace_id: str | None = None,
) -> str:
    """批量结果保存为统一格式 JSON

    格式：
    {
      "metadata": { ... },
      "results": [ ... ]
    }
    """
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
) -> str:
    """单条结果保存为统一格式 JSON"""
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
    """批量结果保存为 CSV

    返回 CSV 文件路径
    """
    _ensure_dir()
    path = str(OUTPUT_DIR / f"{prefix}_{uuid.uuid4().hex[:6]}.csv")

    if not results:
        logger.warning("save_csv_empty")
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        return path

    # 展平数据
    flat: list[dict] = []
    for item in results:
        meta = item.get("metadata", {})
        answers = item.get("answers", item.get("result", item))
        row = {**meta, **answers}
        flat.append(row)

    fields = list(flat[0].keys())
    try:
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(flat)
        logger.info("csv_saved path=%s rows=%d", path, len(flat))
    except OSError as exc:
        logger.error("save_csv_failed path=%s error=%s", path, exc)
        raise

    return path


# ─── 查询 & 清理 ───────────────────────────────────────────────


def list_output_files(pattern: str = "batch_decision_*.json") -> list[Path]:
    """列出输出目录中的文件，按修改时间倒序"""
    _ensure_dir()
    files = list(OUTPUT_DIR.glob(pattern))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files


def clean_old_files(
    pattern: str = "batch_decision_*.json",
    keep_count: int | None = None,
) -> int:
    """清理旧文件，只保留最近 keep_count 个

    Returns:
        已删除的文件数量
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
    """清空所有输出文件

    Returns:
        已删除的文件数量
    """
    _ensure_dir()
    files = list(OUTPUT_DIR.glob(pattern))
    for f in files:
        f.unlink()
    logger.info("all_cleared count=%d", len(files))
    return len(files)