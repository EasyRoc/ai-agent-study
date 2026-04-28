"""
混合检索：向量路 + BM25 路，**RRF（Reciprocal Rank Fusion）** 融合 id 后按分数截断；无 Milvus 时回退为仅 BM25。

与 LangChain `EnsembleRetriever` 等效思路不同：此处融合公式在代码中显式可见，便于周计划「可解释」要求。
"""
from __future__ import annotations

import logging
import os
from collections import defaultdict
from dataclasses import dataclass
from week05.bm25_index import keyword_search_top

logger = logging.getLogger(__name__)

# RRF 常数 k，文献常用 60
_DEFAULT_RRF_K = 60


@dataclass(frozen=True)
class RetrievedPair:
    id: str
    text: str


def rrf_fuse(
    ranked_id_lists: list[list[str]],
    rrf_k: int | None = None,
) -> list[tuple[str, float]]:
    k0 = rrf_k if rrf_k is not None else int(os.environ.get("RAG_RRF_K", str(_DEFAULT_RRF_K)))
    acc: dict[str, float] = defaultdict(float)
    for lst in ranked_id_lists:
        for rank, did in enumerate(lst, start=1):
            if not did:
                continue
            acc[str(did)] += 1.0 / (k0 + rank)
    return sorted(acc.items(), key=lambda x: -x[1])


def _vector_id_list(question: str, k: int) -> list[str]:
    from week03.api import _vectorstore

    try:
        vs = _vectorstore()
        pairs = vs.similarity_search_with_score(question, k=k)
    except Exception:
        logger.warning("混合检索-向量路不可用，本路为空", exc_info=True)
        return []
    out: list[str] = []
    for doc, _ in pairs:
        meta = doc.metadata or {}
        did = getattr(doc, "id", None)
        cid = meta.get("id") or meta.get("pk") or (str(did) if did is not None else "")
        if str(cid or "").strip():
            out.append(str(cid).strip())
    return out


def _id_to_text() -> dict[str, str]:
    from week03.corpus_chunks import list_chunk_id_text

    return {i: t for i, t in list_chunk_id_text()}


def hybrid_search(
    question: str,
    k_vec: int,
    k_kw: int,
    k_out: int,
) -> list[RetrievedPair]:
    """
    - 两路各取 k_vec / k_kw 个 id 参与 RRF，最终输出 k_out 条（有文本即来自语料主数据）。
    """
    q = (question or "").strip()
    if not q:
        return []
    v_ids = _vector_id_list(q, max(1, k_vec))
    kw = keyword_search_top(q, max(1, k_kw))
    kw_ids = [t[0] for t in kw]
    rrf = rrf_fuse([v_ids, kw_ids], rrf_k=None)[: max(1, k_out)]
    by_text = _id_to_text()
    res: list[RetrievedPair] = []
    for did, _sc in rrf:
        t = by_text.get(did, "")
        if t:
            res.append(RetrievedPair(id=did, text=t))
        if len(res) >= k_out:
            break
    if res:
        return res
    # 全失败时：至少尝试纯向量
    v2 = _vector_id_list(q, k_out)
    for did in v2:
        t = by_text.get(did, "")
        if t:
            res.append(RetrievedPair(id=did, text=t))
        if len(res) >= k_out:
            break
    return res
