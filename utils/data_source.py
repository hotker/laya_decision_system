"""
输入数据源
==========
支持从 JSON/CSV/stdin 读取决策数据，而非硬编码

使用方式：
    from data_source import load_data

    # 从 JSON 文件加载
    data = load_data("data.json")

    # 从 CSV 文件加载（指定文本列）
    data = load_data("data.csv", text_column="body")

    # 从 stdin 加载（JSON 数组）
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
    """从数据源加载输入数据

    Args:
        source: 文件路径（.json / .csv / "-" 表示 stdin），None 表示使用默认数据
        text_column: CSV 中文本所在的列名

    Returns:
        [{"body": "..."}, ...] 或 None（使用默认数据时）
    """
    if source is None:
        return None

    source = source.strip()

    if source == "-":
        return _load_stdin(text_column)

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"数据文件不存在: {source}")

    ext = path.suffix.lower()
    if ext == ".json":
        return _load_json(path, text_column)
    elif ext in (".csv", ".tsv"):
        return _load_csv(path, text_column, sep="," if ext == ".csv" else "\t")
    else:
        raise ValueError(f"不支持的数据格式: {ext}（支持 .json / .csv / .tsv）")


def _load_stdin(text_column: str) -> list[dict[str, Any]]:
    """从 stdin 读取 JSON 数组"""
    text = sys.stdin.read().strip()
    if not text:
        return []

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"stdin JSON 解析失败: {exc}")

    return _normalize_data(data, text_column)


def _load_json(path: Path, text_column: str) -> list[dict[str, Any]]:
    """从 JSON 文件加载"""
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 解析失败: {exc}")

    return _normalize_data(data, text_column)


def _normalize_data(data: Any, text_column: str) -> list[dict[str, Any]]:
    """统一处理 JSON 数据，提取 body 字段"""
    if isinstance(data, list):
        return _normalize_list(data, text_column)
    elif isinstance(data, dict):
        # 兼容输出格式：{"results": [...]} 或 {"data": [...]}
        for key in ("results", "data", "items"):
            if key in data and isinstance(data[key], list):
                return _normalize_list(data[key], text_column)
        # 单条记录
        body = data.get(text_column, data.get("body", data.get("text", "")))
        if body:
            return [{"body": body, **{k: v for k, v in data.items() if k not in (text_column, "body", "text")}}]
        return []
    else:
        raise ValueError("JSON 数据期望数组或对象")


def _normalize_list(items: list, text_column: str) -> list[dict[str, Any]]:
    """从列表中提取 body"""
    results: list[dict] = []
    for item in items:
        if isinstance(item, str):
            results.append({"body": item})
        elif isinstance(item, dict):
            body = item.get(text_column, item.get("body", item.get("text", "")))
            if body:
                extra = {k: v for k, v in item.items() if k not in (text_column, "body", "text")}
                results.append({"body": body, **extra})
    return results


def _load_csv(path: Path, text_column: str, sep: str) -> list[dict[str, Any]]:
    """从 CSV 文件加载"""
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
    """将处理结果写入文件"""
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
        raise ValueError(f"不支持的输出格式: {fmt}")

    logger.info("output_saved path=%s format=%s count=%d", out_path, fmt, len(data))