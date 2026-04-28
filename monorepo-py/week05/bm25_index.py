"""
第 5 周：在语料分块上建 BM25；与第 3 周 `list_chunk_id_text()` 的 id 一致，便于与向量结果 RRF 融合。

未用 LangChain EnsembleRetriever等封装：本仓为教学可读性，BM25 直建 + RRF 手抄公式，见 week05/README.md。
"""
from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

_lock = threading.RLock()
_state: tuple["BM25Okapi", list[str], dict[str, str]] | None = None


def _tokenize(text: str) -> list[str]:
    import jieba

    t = (text or "").strip()
    if not t:
        return []
    toks = [x.strip() for x in jieba.lcut(t) if x and x.strip()]
    return toks or ["\u00a0"]  # 避免空条导致 BM25 异常


def _ensure() -> tuple["BM25Okapi", list[str], dict[str, str]] | None:
    global _state
    with _lock:
        if _state is not None:
            return _state
        from week03.corpus_chunks import list_chunk_id_text
        from rank_bm25 import BM25Okapi

        pairs = list_chunk_id_text()
        if not pairs:
            _state = None
            return None
        doc_ids = [p[0] for p in pairs]
        by_id = {p[0]: p[1] for p in pairs}
        tokenized = [_tokenize(p[1]) for p in pairs]
        try:
            bm = BM25Okapi(tokenized)
        except Exception:
            logger.exception("BM25 索引构建失败")
            _state = None
            return None
        _state = (bm, doc_ids, by_id)
        return _state


def keyword_search_top(q: str, k: int) -> list[tuple[str, float, str]]:
    """
    返回 (chunk_id, bm25 相对分, text)，按分从高到低，最多 k 条。
    """
    st = _ensure()
    if st is None or not (q or "").strip():
        return []
    bm, _doc_ids, by_id = st
    toks = _tokenize(q)
    if not toks:
        return []
    k = max(1, k)
    scores = list(bm.get_scores(toks))
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    out: list[tuple[str, float, str]] = []
    for i in ranked:
        did = _doc_ids[i]
        out.append((did, float(scores[i]), by_id.get(did, "")))
    return out
