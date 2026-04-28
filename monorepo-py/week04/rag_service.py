"""
第 4 周：retrieve（第 3 周 Milvus，可调大 recall）→ 可选 Rerank（qwen3-vl-rerank）→
拼 prompt → LLM → Pydantic 结构化输出 citation_ids → 映射为 {id, excerpt}。

L2 企业知识（Milvus）；L0 短期对话见 `session_memory`（仅 prompt 注入，不写向量库）。
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from week04.rerank_qwen import rerank_text_indices
from week04.session_memory import append_turn, get_history_for_prompt

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    text: str


class RagLlmStructured(BaseModel):
    """与课表一致：优先框架 structured output，而非手写正则 JSON。"""

    answer: str = Field(
        description=(
            "用自然、连贯的中文，针对用户问题做归纳后作答；内容须能由【参考资料】支撑，但 "
            "不得把某条资料整段复制粘贴为回答；要提炼要点、组织成对话式说明，无把握时说明无法从资料中得出"
        )
    )
    citation_ids: list[str] = Field(
        default_factory=list,
        description="你实际引用过的资料条 id，必须来自用户消息中以 [id] 标出的标识，不要编造 id",
    )


RAG_SYSTEM = """你是企业内部知识助手。你只能根据用户消息中的【参考资料】理解事实后再作答，不能把参考资料原文当作回答输出。

要求：
1. 先根据问题从【参考资料】中提取与问题相关的信息，再**用自己的话归纳、转述、总结**；`answer` 须是针对问题的说明性文字，**禁止**大段或全文照搬某条 [id] 下的原文。
2. 若参考资料不足以回答，直接说「根据现有知识库未找到相关制度说明」等，**不要**编造、不要补常识当作制度事实。
3. 不输出与问题无关的展开；不罗列向量检索片段、不逐条贴原文。
4. 若消息中带有【近期对话】，可藉此理解多轮指代与省略，但**制度、数字、条款**一律以当次【参考资料】或明确拒答为准；不要假定历史对话里的表述在本次仍然成立。
5. 回答使用中文，简洁清晰、面向用户可读懂。"""


def _build_llm() -> ChatOpenAI:
    key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("AI_DASHSCOPE_API_KEY")
    if not key:
        raise RuntimeError("请设置 DASHSCOPE_API_KEY")
    model = os.environ.get("LLM_MODEL", "qwen-turbo")
    return ChatOpenAI(
        model=model,
        temperature=float(os.environ.get("RAG_TEMPERATURE", "0.3")),
        api_key=key,
        base_url=os.environ.get("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        timeout=float(os.environ.get("RAG_LLM_TIMEOUT_SEC", "90")),
    )


def _recall_k(wanted_final: int) -> int:
    """向量初检条数；默认约 2× 最终条数、不少于 8，且受 qwen3-vl-rerank 单请求上限 100 约束。"""
    env = os.environ.get("RAG_RECALL_TOP_K")
    if env is not None and str(env).strip() != "":
        try:
            v = int(str(env).strip())
        except ValueError:
            v = max(8, wanted_final * 2)
    else:
        v = max(8, wanted_final * 2)
    v = min(100, max(v, wanted_final))
    return v


def _hybrid_enabled() -> bool:
    return os.environ.get("RAG_HYBRID_ENABLED", "true").lower() in ("1", "true", "yes", "on")


def _retrieve_chunks(question: str, top_k: int) -> list[RetrievedChunk]:
    if _hybrid_enabled():
        from week05.hybrid import hybrid_search

        try:
            k_kw = int(os.environ.get("RAG_HYBRID_KW", "0").strip() or "0")
        except ValueError:
            k_kw = 0
        if k_kw <= 0:
            k_kw = max(4, min(top_k, 32))
        pairs = hybrid_search(
            question,
            k_vec=top_k,
            k_kw=k_kw,
            k_out=top_k,
        )
        if pairs:
            return [RetrievedChunk(id=p.id, text=p.text) for p in pairs]
        logger.info("run_rag 混合检索无结果，回退纯向量路")

    # 避免与 week03.api 顶层 import 循环：在函数内再 import
    from week03.api import _vectorstore

    vs = _vectorstore()
    pairs = vs.similarity_search_with_score(question, k=top_k)
    out: list[RetrievedChunk] = []
    for doc, _dist in pairs:
        meta = doc.metadata or {}
        did = getattr(doc, "id", None)
        cid = meta.get("id") or meta.get("pk") or (str(did) if did is not None else "")
        if not cid:
            continue
        out.append(RetrievedChunk(id=str(cid), text=doc.page_content or ""))
    return out


def _format_refs(chunks: list[RetrievedChunk]) -> str:
    lines = []
    for c in chunks:
        lines.append(f"[{c.id}] {c.text.strip()}")
    return "\n".join(lines)


def _map_citations(ids: list[str], by_id: dict[str, str], max_excerpt: int = 320) -> list[dict[str, str]]:
    seen: set[str] = set()
    rows: list[dict[str, str]] = []
    for i in ids:
        i = str(i).strip()
        if not i or i in seen:
            continue
        seen.add(i)
        text = by_id.get(i, "")
        excerpt = (text[:max_excerpt] + "…") if len(text) > max_excerpt else text
        rows.append({"id": i, "excerpt": excerpt})
    return rows


def _q_preview(s: str, n: int = 120) -> str:
    s = s.replace("\n", " ").strip()
    if len(s) <= n:
        return s
    return s[:n] + "…"


def run_rag(
    question: str, top_k: int = 4, session_id: str | None = None
) -> tuple[str, list[dict[str, str]], list[str]]:
    """
    返回 (answer, citations, cited_ids)：
    - citations：送入 LLM 的检索条数一致的全量 {id, excerpt}（对账 top_k）；
    - cited_ids：模型在 citation_ids 里声明引用过的 id 子集（可少于 citations）。
    """
    if session_id:
        logger.info("run_rag start sessionId=%s", session_id)

    q = question.strip()
    if not q:
        logger.info("run_rag 跳过：问题为空")
        return "问题为空。", [], []

    recall = _recall_k(top_k)
    logger.info("run_rag 入参 top_k=%s recall_k=%s q_preview=%r", top_k, recall, _q_preview(q))

    chunks = _retrieve_chunks(q, top_k=recall)
    if not chunks:
        logger.info("run_rag 无检索结果：recall_k=%s", recall)
        _no_hits = (
            "根据现有知识库未检索到相关资料，无法基于制度文本作答。请尝试换关键词或确认已完成入库（ingest）。"
        )
        append_turn(session_id, q, _no_hits)
        return _no_hits, [], []

    n_final = min(top_k, len(chunks))
    pre_ids = [c.id for c in chunks]
    logger.info("run_rag 向量初检条数=%s n_final(送入 LLM)=%s", len(chunks), n_final)
    _rerank_on = os.environ.get("RAG_RERANK_ENABLED", "true").lower() in ("1", "true", "yes", "on")
    if _rerank_on and n_final > 0:
        idxs = rerank_text_indices(q, [c.text for c in chunks], top_n=n_final)
        if idxs:
            chunks = [chunks[i] for i in idxs]
            logger.info(
                "run_rag rerank 完成 top_n=%s 模型=%s chunk_ids 顺序(重排)=%s",
                n_final,
                os.environ.get("RAG_RERANK_MODEL", "qwen3-vl-rerank"),
                [c.id for c in chunks],
            )
        else:
            chunks = chunks[:n_final]
            logger.info(
                "run_rag rerank 回退为向量序 top_n=%s 初检数=%s chunk_ids(向量序前段)=%s",
                n_final,
                len(pre_ids),
                [c.id for c in chunks],
            )
    else:
        chunks = chunks[:n_final]
        logger.info(
            "run_rag 未开 rerank top_n=%s 初检数=%s chunk_ids(向量序)=%s",
            n_final,
            len(pre_ids),
            [c.id for c in chunks],
        )

    by_id = {c.id: c.text for c in chunks}
    refs_block = _format_refs(chunks)
    _hist = get_history_for_prompt(session_id)
    if _hist:
        logger.info("run_rag 已注入 L0 短期记忆 sessionId=%s 有效轮数(粗估)=%s", session_id, _hist.count("用户："))
    _core = f"""【参考资料】（每条以 [id] 开头；citation_ids 里填你实际依据的 id）：
{refs_block}

用户问题：{q}

【作答要求】请根据上述资料中与问题相关的内容作答：先理解再归纳，用完整句子说明结论；不要逐条复述资料原文，也不要把某一条资料的全文当作 answer 输出。"""
    user_prompt = f"{_hist}{_core}" if _hist else _core

    model = os.environ.get("LLM_MODEL", "qwen-turbo")
    llm = _build_llm()
    chain = llm.with_structured_output(RagLlmStructured, include_raw=False)
    logger.info(
        "run_rag 调用 LLM model=%s user_prompt_chars=%s refs_block_chars=%s",
        model,
        len(user_prompt),
        len(refs_block),
    )
    try:
        structured = chain.invoke(
            [SystemMessage(content=RAG_SYSTEM), HumanMessage(content=user_prompt)]
        )
        if isinstance(structured, dict):
            structured = RagLlmStructured.model_validate(structured)
    except Exception:
        logger.exception("RAG LLM 调用或结构化解析失败 (model=%s prompt_chars=%s)", model, len(user_prompt))
        err_cites = [c for c in _map_citations([c.id for c in chunks], by_id) if c.get("excerpt")]
        return (
            "生成回答时发生错误，请稍后重试。",
            err_cites,
            [],
        )

    answer = (structured.answer or "").strip()
    raw_m = [str(x).strip() for x in (structured.citation_ids or []) if str(x).strip()]
    seen_m: set[str] = set()
    cited_ids: list[str] = []
    for i in raw_m:
        if i in by_id and (by_id[i] or "").strip() and i not in seen_m:
            cited_ids.append(i)
            seen_m.add(i)
    if not raw_m:
        logger.info("run_rag 模型未返回 citation_ids，cited_ids 为空；citations 仍为全量检索条")
    all_rows = _map_citations([c.id for c in chunks], by_id)
    citations = [c for c in all_rows if c.get("excerpt")]

    logger.info(
        "run_rag 结束 answer_chars=%s citations(全量)=%s cited_ids(模型)=%s",
        len(answer),
        len(citations),
        cited_ids,
    )
    out = answer or "（无正文）"
    append_turn(session_id, q, out)
    return out, citations, cited_ids
