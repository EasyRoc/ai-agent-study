"""
DashScope 文本/多模态重排：默认 qwen3-vl-rerank（与阿里云 Model Studio 文档一致）。

失败时返回 None，由调用方回退为向量检索顺序，避免整条 RAG 挂死。
"""
from __future__ import annotations

import logging
import os
from http import HTTPStatus

logger = logging.getLogger(__name__)


def _dashscope_key() -> str | None:
    return os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("AI_DASHSCOPE_API_KEY")


def rerank_text_indices(
    question: str,
    documents: list[str],
    top_n: int,
) -> list[int] | None:
    """
    按相关性对 documents 重排，返回「原始下标」列表（长度不超过 top_n，顺序为相关性从高到低）。

    调用失败、未安装 dashscope、或入参不合法时返回 None。
    """
    q = (question or "").strip()
    if not q or not documents:
        return None
    n = min(max(1, top_n), len(documents))
    key = _dashscope_key()
    if not key:
        logger.warning("Rerank 跳过：未设置 DASHSCOPE_API_KEY")
        return None

    try:
        import dashscope
    except ImportError:
        logger.warning("Rerank 跳过：未安装 dashscope，请 pip install -r requirements.txt")
        return None

    dashscope.api_key = key
    model = os.environ.get("RAG_RERANK_MODEL", "qwen3-vl-rerank").strip() or "qwen3-vl-rerank"
    instruct = os.environ.get("RAG_RERANK_INSTRUCT", "").strip()

    # qwen3-vl-rerank：query 为文本时用 {"text": ...}；documents 为纯文本文档时可直接用字符串列表
    kwargs: dict = {
        "model": model,
        "query": {"text": q},
        "documents": documents,
        "top_n": n,
        "return_documents": True,
    }
    if instruct:
        kwargs["instruct"] = instruct

    try:
        resp = dashscope.TextReRank.call(**kwargs)
    except Exception:
        logger.exception("Rerank TextReRank 调用异常")
        return None

    if resp.status_code != HTTPStatus.OK:
        logger.warning("Rerank 非成功状态: status_code=%s body=%s", resp.status_code, resp)
        return None

    out = getattr(resp, "output", None) or {}
    results = out.get("results") if isinstance(out, dict) else None
    if not results:
        logger.warning("Rerank 返回空 results: %s", resp)
        return None

    indices: list[int] = []
    for r in results:
        if not isinstance(r, dict):
            continue
        idx = r.get("index")
        if idx is None:
            continue
        try:
            i = int(idx)
        except (TypeError, ValueError):
            continue
        if 0 <= i < len(documents) and i not in indices:
            indices.append(i)
        if len(indices) >= n:
            break

    if not indices:
        return None
    return indices
