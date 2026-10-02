"""
异步 HTTP 客户端
================
基于 httpx 的异步请求支持，用于高并发批量场景

使用方式：
    from async_http_client import async_make_predict_request, async_batch_concurrent
    result = await async_make_predict_request("文本内容", questions={...})
    results = await async_batch_concurrent(states, questions)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

try:
    import httpx

    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

logger = logging.getLogger(__name__)


def require_httpx() -> None:
    """确保 httpx 已安装"""
    if not _HAS_HTTPX:
        raise RuntimeError(
            "async HTTP client requires httpx. "
            "Install it with: pip install httpx>=0.25.0"
        )


async def async_make_predict_request(
    state: str,
    questions: dict,
    model: Optional[str] = None,
    task: Optional[str] = None,
    lang: Optional[str] = None,
    timeout: Optional[float] = None,
    trace_id: Optional[str] = None,
) -> dict[str, Any]:
    """异步发送单条预测请求

    使用 httpx 非阻塞发送，适合高并发场景。

    Args:
        state: 输入文本
        questions: 问题定义
        model: 模型名称
        task: 任务类型
        lang: 语言代码
        timeout: 超时秒数
        trace_id: 追踪 ID

    Returns:
        服务响应字典，失败时返回 {"error": str}
    """
    require_httpx()
    from config.config import get_config

    cfg = get_config()
    url = f"{cfg.server.base_url}/predict"
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

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(cfg.server.timeout),
            limits=httpx.Limits(max_connections=50),
        ) as client:
            resp = await client.post(url, json=payload)

            if resp.status_code != 200:
                logger.error(
                    "async_predict_http_error status=%d trace_id=%s",
                    resp.status_code,
                    trace_id,
                )
                return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

            return resp.json()

    except httpx.TimeoutException as exc:
        logger.error("async_predict_timeout trace_id=%s", trace_id)
        return {"error": f"Timeout after {timeout}s"}
    except httpx.ConnectionError as exc:
        return {"error": f"Connection error: {exc}"}
    except ValueError as exc:
        return {"error": f"Invalid JSON: {exc}"}
    except Exception as exc:
        logger.error("async_predict_error trace_id=%s error=%s", trace_id, exc)
        return {"error": str(exc)}


async def async_batch_concurrent(
    states: list[dict],
    questions: dict,
    model: Optional[str] = None,
    timeout: Optional[float] = None,
    trace_id: Optional[str] = None,
) -> dict[str, Any]:
    """异步批量预测请求（并发执行）

    按 MAX_CONCURRENT_REQUESTS 并发发送单条请求。

    Args:
        states: 状态列表，每项含 "body" 字段
        questions: 问题定义
        model: 模型名称
        timeout: 超时秒数
        trace_id: 追踪 ID

    Returns:
        {"results": [...], "errors": [...], "progress": {...}}
    """
    require_httpx()
    from config.config import get_config

    cfg = get_config()
    concurrency = cfg.performance.max_concurrent_requests

    async def _one(i: int, state: dict) -> dict[str, Any]:
        tid = f"{trace_id}-{i}" if trace_id else None
        body = state.get("body", "") if isinstance(state, dict) else str(state)
        result = await async_make_predict_request(body, questions, model=model, trace_id=tid)
        if "error" in result:
            return {"index": i, "state": state, "error": result["error"]}
        return {"index": i, "state": state, "result": result}

    sem = asyncio.Semaphore(concurrency)

    async def _bounded(i: int, state: dict) -> dict[str, Any]:
        async with sem:
            return await _one(i, state)

    tasks = [_bounded(i, s) for i, s in enumerate(states)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理异常结果
    processed = []
    for r in results:
        if isinstance(r, Exception):
            processed.append({"index": 0, "state": {}, "error": str(r)})
        else:
            processed.append(r)

    # 按 index 排序
    processed.sort(key=lambda x: x.get("index", 0))

    succeeded = [r for r in processed if "error" not in r]
    errors = [r for r in processed if "error" in r]

    return {
        "results": succeeded,
        "errors": errors,
        "progress": {
            "total": len(states),
            "succeeded": len(succeeded),
            "failed": len(errors),
        },
    }