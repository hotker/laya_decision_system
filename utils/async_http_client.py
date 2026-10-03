"""
Async HTTP Client
=================
Asynchronous HTTP client based on httpx for high-concurrency batch processing

Features:
  - Persistent async client instance (connection pooling)
  - Exponential backoff retry for 429/5xx errors
  - Structured trace_id injection

Usage:
    from async_http_client import async_make_predict_request, async_batch_concurrent
    result = await async_make_predict_request("text content", questions={...})
    await async_close_client()
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import httpx

from config.config import get_config

logger = logging.getLogger(__name__)

# ─── Async Session Management ───────────────────────────────────

_async_client: httpx.AsyncClient | None = None
_async_lock = asyncio.Lock()


async def _get_async_client() -> httpx.AsyncClient:
    """Get or create persistent async client (connection pooling)."""
    global _async_client
    if _async_client is not None:
        return _async_client

    async with _async_lock:
        if _async_client is None:
            cfg = get_config()
            _async_client = httpx.AsyncClient(
                base_url=cfg.server.base_url,
                timeout=httpx.Timeout(cfg.server.timeout),
                follow_redirects=True,
            )
        return _async_client


async def async_close_client() -> None:
    """Close persistent async client. Mainly for testing/shutdown."""
    global _async_client
    if _async_client is not None:
        await _async_client.aclose()
        _async_client = None


# ─── Async Single Request ───────────────────────────────────────


async def async_make_predict_request(
    state: str,
    questions: dict,
    model: Optional[str] = None,
    task: Optional[str] = None,
    lang: Optional[str] = None,
    timeout: Optional[int] = None,
    trace_id: Optional[str] = None,
    max_retries: Optional[int] = None,
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
        max_retries: Override retry count (default from config)

    Returns:
        Service response dict, returns {"error": str} on failure
    """
    cfg = get_config()
    client = await _get_async_client()
    timeout = timeout or cfg.server.timeout
    model = model or cfg.server.model
    retries = max_retries if max_retries is not None else cfg.performance.retry_times
    delay = cfg.performance.retry_delay
    backoff = cfg.performance.retry_backoff_factor

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

    for attempt in range(retries + 1):
        try:
            logger.debug(
                "async_predict_request attempt=%d url=/predict trace_id=%s",
                attempt + 1,
                trace_id,
            )
            resp = await client.post("/predict", json=payload, timeout=timeout)

            if resp.status_code == 200:
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

            # Retryable HTTP errors
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = delay * (backoff ** attempt)
                logger.warning(
                    "async_predict_retry attempt=%d status=%d delay=%.1fs trace_id=%s",
                    attempt + 1,
                    resp.status_code,
                    wait,
                    trace_id,
                )
                await asyncio.sleep(wait)
                continue

            logger.error(
                "async_predict_http_error status=%d trace_id=%s", resp.status_code, trace_id
            )
            return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

        except (httpx.TimeoutException, httpx.ReadTimeout, httpx.WriteTimeout) as exc:
            if attempt < retries:
                wait = delay * (backoff ** attempt)
                logger.warning(
                    "async_predict_timeout_retry attempt=%d delay=%.1fs trace_id=%s",
                    attempt + 1,
                    wait,
                    trace_id,
                )
                await asyncio.sleep(wait)
                continue
            logger.error("async_predict_timeout trace_id=%s error=%s", trace_id, exc)
            return {"error": f"Timeout after {timeout}s"}

        except httpx.ConnectError as exc:
            if attempt < retries:
                wait = delay * (backoff ** attempt)
                logger.warning(
                    "async_predict_conn_retry attempt=%d delay=%.1fs trace_id=%s",
                    attempt + 1,
                    wait,
                    trace_id,
                )
                await asyncio.sleep(wait)
                continue
            logger.error("async_predict_conn_error trace_id=%s error=%s", trace_id, exc)
            return {"error": f"Connection error: {exc}"}

        except httpx.RequestError as exc:
            logger.error("async_predict_error trace_id=%s error=%s", trace_id, exc)
            return {"error": str(exc)}

        except Exception as exc:
            logger.error("async_predict_unexpected trace_id=%s error=%s", trace_id, exc)
            return {"error": str(exc)}

    # Should not reach here, but safety net
    return {"error": "Retry limit exceeded"}


# ─── Async Batch Request ────────────────────────────────────────


async def async_batch_concurrent(
    states: list[dict],
    questions: dict,
    max_concurrent: int | None = None,
    max_retries: Optional[int] = None,
) -> dict[str, Any]:
    """Execute batch requests concurrently

    Args:
        states: State list
        questions: Question definition
        max_concurrent: Maximum concurrent requests
        max_retries: Override retry count per request

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
                max_retries=max_retries,
            )

    tasks = [_make_request(state) for state in states]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error("async_batch_task_error index=%d error=%s", i, result)
            processed_results.append({"error": f"Task {i} failed: {result}", "index": i})
        else:
            processed_results.append(result)

    return {"results": processed_results, "total": len(states)}