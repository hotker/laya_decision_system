"""
Async HTTP Client
=================
Asynchronous HTTP client based on httpx for high-concurrency batch processing

Usage:
    from async_http_client import async_make_predict_request, async_batch_concurrent
    result = await async_make_predict_request("text content", questions={...})
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import httpx

from config.config import get_config

logger = logging.getLogger(__name__)


# ─── Async Session Management ───────────────────────────────────


def _get_async_client() -> httpx.AsyncClient:
    """Get async HTTP client instance"""
    cfg = get_config()
    return httpx.AsyncClient(
        base_url=cfg.server.base_url,
        timeout=httpx.Timeout(cfg.server.timeout),
        follow_redirects=True,
    )


# ─── Async Single Request ───────────────────────────────────────


async def async_make_predict_request(
    state: str,
    questions: dict,
    model: Optional[str] = None,
    task: Optional[str] = None,
    lang: Optional[str] = None,
    timeout: Optional[int] = None,
    trace_id: Optional[str] = None,
) -> dict[str, Any]:
    """Send single prediction request asynchronously

    Args:
        state: Input text/state
        questions: Question definition
        model: Model name
        task: Task type
        lang: Language code
        timeout: Timeout in seconds
        trace_id: Trace ID

    Returns:
        Service response dict, returns {"error": str} on failure
    """
    cfg = get_config()
    client = _get_async_client()
    url = "/predict"
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
        logger.debug("async_predict_request url=%s trace_id=%s", url, trace_id)
        resp = await client.post(url, json=payload, timeout=timeout)

        if resp.status_code != 200:
            logger.error(
                "async_predict_http_error status=%d trace_id=%s", resp.status_code, trace_id
            )
            return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

        try:
            result = resp.json()
            logger.debug(
                "async_predict_response trace_id=%s result_keys=%s",
                trace_id,
                list(result.keys()),
            )
            return result
        except ValueError as exc:
            logger.error("async_invalid_json trace_id=%s error=%s", trace_id, exc)
            return {"error": f"Invalid JSON response: {exc}"}

    except httpx.TimeoutException as exc:
        logger.error("async_predict_timeout trace_id=%s error=%s", trace_id, exc)
        return {"error": f"Timeout after {timeout}s"}
    except httpx.ConnectError as exc:
        logger.error("async_predict_conn_error trace_id=%s error=%s", trace_id, exc)
        return {"error": f"Connection error: {exc}"}
    except httpx.RequestError as exc:
        logger.error("async_predict_error trace_id=%s error=%s", trace_id, exc)
        return {"error": str(exc)}
    except Exception as exc:
        logger.error("async_predict_unexpected trace_id=%s error=%s", trace_id, exc)
        return {"error": str(exc)}
    finally:
        await client.aclose()


# ─── Async Batch Request ────────────────────────────────────────


async def async_batch_concurrent(
    states: list[dict],
    questions: dict,
    max_concurrent: int | None = None,
) -> dict[str, Any]:
    """Execute batch requests concurrently

    Args:
        states: State list
        questions: Question definition
        max_concurrent: Maximum concurrent requests

    Returns:
        Dict containing "results" list
    """
    cfg = get_config()
    if max_concurrent is None:
        max_concurrent = cfg.performance.max_concurrent_requests

    semaphore = asyncio.Semaphore(max_concurrent)

    async def _make_request(state: dict) -> dict[str, Any]:
        async with semaphore:
            return await async_make_predict_request(
                state.get("body", str(state)),
                questions,
            )

    tasks = [_make_request(state) for state in states]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error("async_batch_task_error index=%d error=%s", i, result)
            processed_results.append({"error": str(result)})
        else:
            processed_results.append(result)

    return {"results": processed_results, "total": len(states)}