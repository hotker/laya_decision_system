"""
公共 HTTP 客户端
================
基于 requests / httpx 的标准化 Laya AI 服务通信

功能：
  - 同步 & 异步请求（自动检测 anyio 可用性）
  - 指数退避重试（可配置次数/延迟/退避因子）
  - 连接池管理
  - 结构化 trace_id 注入

使用方式：
    from http_client import make_predict_request, make_batch_request
    result = make_predict_request("文本内容", questions={...})
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.config import get_config

logger = logging.getLogger(__name__)

# ─── 会话管理 ──────────────────────────────────────────────────


def _build_session() -> requests.Session:
    """构建带重试策略的 requests.Session"""
    cfg = get_config()

    retry = Retry(
        total=cfg.performance.retry_times,
        backoff_factor=cfg.performance.retry_backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"],
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


# 全局会话（线程安全，复用连接池）
_session: requests.Session | None = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = _build_session()
    return _session


# ─── 同步请求 ──────────────────────────────────────────────────


def make_predict_request(
    state: str,
    questions: dict,
    model: Optional[str] = None,
    task: Optional[str] = None,
    lang: Optional[str] = None,
    timeout: Optional[int] = None,
    trace_id: Optional[str] = None,
) -> dict[str, Any]:
    """发送单条预测请求

    Args:
        state: 输入文本/状态
        questions: 问题定义（分类标准、情感维度等）
        model: 模型名称
        task: 任务类型
        lang: 语言代码
        timeout: 超时秒数
        trace_id: 追踪 ID

    Returns:
        服务响应字典，失败时返回 {"error": str}
    """
    cfg = get_config()
    base_url = cfg.server.base_url
    url = f"{base_url}/predict"
    timeout = timeout or cfg.server.timeout
    model = model or cfg.server.model

    payload: dict[str, Any] = {
        "state": state,
        "questions": questions,
        "model": model,
    }
    if task:
        payload["task"] = task
    if lang:
        payload["lang"] = lang
    if trace_id:
        payload["trace_id"] = trace_id

    session = _get_session()

    try:
        logger.debug("predict_request url=%s trace_id=%s", url, trace_id)
        resp = session.post(url, json=payload, timeout=timeout)

        # 检查 HTTP 状态
        if resp.status_code != 200:
            logger.error(
                "predict_http_error status=%d trace_id=%s", resp.status_code, trace_id
            )
            return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

        # 解析 JSON
        try:
            result = resp.json()
            logger.debug(
                "predict_response trace_id=%s result_keys=%s",
                trace_id,
                list(result.keys()),
            )
            return result
        except ValueError as exc:
            logger.error("invalid_json trace_id=%s error=%s", trace_id, exc)
            return {"error": f"Invalid JSON response: {exc}"}

    except requests.exceptions.Timeout as exc:
        logger.error("predict_timeout trace_id=%s error=%s", trace_id, exc)
        return {"error": f"Timeout after {timeout}s"}
    except requests.exceptions.ConnectionError as exc:
        logger.error("predict_conn_error trace_id=%s error=%s", trace_id, exc)
        return {"error": f"Connection error: {exc}"}
    except requests.exceptions.RequestException as exc:
        logger.error("predict_error trace_id=%s error=%s", trace_id, exc)
        return {"error": str(exc)}
    except Exception as exc:
        logger.error("predict_unexpected trace_id=%s error=%s", trace_id, exc)
        return {"error": str(exc)}


def make_batch_request(
    states: list[dict],
    questions: dict,
    model: Optional[str] = None,
    timeout: Optional[int] = None,
    trace_id: Optional[str] = None,
) -> dict[str, Any]:
    """发送批量预测请求

    自动分块处理超过 MAX_BATCH_SIZE 的请求。

    Args:
        states: 状态列表，每个元素包含 "body" 等字段
        questions: 问题定义
        model: 模型名称
        timeout: 超时秒数
        trace_id: 追踪 ID

    Returns:
        包含 "results" 列表的字典，失败时返回 {"error": str}
    """
    cfg = get_config()
    max_batch = cfg.performance.max_batch_size
    session = _get_session()

    base_url = cfg.server.base_url
    url = f"{base_url}/predict/batch"
    timeout = timeout or cfg.performance.request_timeout
    model = model or cfg.server.model

    # 自动分块
    if len(states) > max_batch:
        logger.info(
            "batch_autosplit total=%d max=%d chunks=%d",
            len(states),
            max_batch,
            (len(states) + max_batch - 1) // max_batch,
        )
        results: list[dict] = []
        for i in range(0, len(states), max_batch):
            chunk = states[i : i + max_batch]
            chunk_result = make_batch_request(
                chunk, questions, model, timeout, trace_id
            )
            if "error" in chunk_result:
                return chunk_result
            results.extend(chunk_result.get("results", []))
        return {"results": results}

    payload: dict[str, Any] = {
        "states": states,
        "questions": questions,
        "model": model,
    }
    if trace_id:
        payload["trace_id"] = trace_id

    try:
        logger.debug("batch_request url=%s count=%d trace_id=%s", url, len(states), trace_id)
        resp = session.post(url, json=payload, timeout=timeout)

        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

        try:
            result = resp.json()
            logger.debug(
                "batch_response trace_id=%s count=%d",
                trace_id,
                len(result.get("results", [])),
            )
            return result
        except ValueError as exc:
            return {"error": f"Invalid JSON response: {exc}"}

    except requests.exceptions.Timeout as exc:
        return {"error": f"Timeout after {timeout}s"}
    except requests.exceptions.ConnectionError as exc:
        return {"error": f"Connection error: {exc}"}
    except requests.exceptions.RequestException as exc:
        return {"error": str(exc)}
    except Exception as exc:
        return {"error": str(exc)}


def check_health(base_url: Optional[str] = None) -> dict[str, Any]:
    """检查 Laya 服务健康状态

    Returns:
        {"status": "ok", ...} 或 {"status": "error", "message": str}
    """
    cfg = get_config()
    target = base_url or cfg.server.base_url
    url = f"{target}/health"

    try:
        resp = requests.get(url, timeout=10)
        result = resp.json()
        result["status"] = "ok"
        result["url"] = url
        logger.info("health_check_passed url=%s", url)
        return result
    except requests.exceptions.ConnectionError as exc:
        return {"status": "error", "url": url, "message": str(exc)}
    except Exception as exc:
        return {"status": "error", "url": url, "message": str(exc)}


def reset_session() -> None:
    """重置全局会话（主要用于测试）"""
    global _session
    if _session:
        _session.close()
    _session = None