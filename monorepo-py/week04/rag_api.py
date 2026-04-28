"""
第 4 周：POST /rag/ask，由 week03.api 挂载到同一 uvicorn（8010）。
"""
from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field, field_validator

from week04.rag_service import run_rag

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parent.parent

router = APIRouter(prefix="/rag", tags=["week04-rag"])


def _load_dotenv() -> None:
    p = _ROOT / ".env"
    if p.is_file():
        load_dotenv(p)
    else:
        load_dotenv()


class RagAskBody(BaseModel):
    # populate_by_name：JSON 可用 topK 或 top_k 等同名字段
    # str_strip_whitespace：全空白 question 在解析阶段即失败，避免无意义 200
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    question: str = Field(..., min_length=1, description="用户问题")
    # 与客户端入参解耦：Pydantic 先允许较大范围，避免误传 topK>10 时直接 422
    # 实际用于检索条数在 rag_ask 中仍钳制在 1～10
    top_k: int = Field(4, ge=1, le=100, alias="topK", description="检索条数 1～100，服务端再限制为 1～10")
    # 可选；传则启用**进程内** L0 短期多轮记忆（与 Milvus 知识库解耦，见 week04.session_memory）
    session_id: str | None = Field(None, alias="sessionId", description="可选；有则多轮同一会话带近期问答摘要，不传则无记忆")

    @field_validator("session_id", mode="before")
    @classmethod
    def _coerce_session_id(cls, v: object) -> str | None:
        if v is None:
            return None
        if isinstance(v, bool):
            return str(v)
        if isinstance(v, int):
            return str(v)
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        if isinstance(v, float):
            return str(v)
        s = str(v).strip()
        return s or None


class CitationItem(BaseModel):
    id: str
    excerpt: str


class RagAskResponse(BaseModel):
    answer: str
    # 与 top_k/召回+重排后送入 LLM 的「参考资料」条数一致
    citations: list[CitationItem]
    # 模型在 structured output 里填的 id；条数可少于 citations（citations 为实际送入 LLM 的全量检索条）
    cited_ids: list[str] = Field(default_factory=list)
    memory_layer: str = "L2_rag"


@router.post("/ask", response_model=RagAskResponse)
def rag_ask(body: RagAskBody) -> RagAskResponse:
    _load_dotenv()
    top_k = max(1, min(10, body.top_k))
    answer, cites, cited_ids = run_rag(
        body.question,
        top_k=top_k,
        session_id=body.session_id,
    )
    return RagAskResponse(
        answer=answer,
        citations=[CitationItem(id=c["id"], excerpt=c["excerpt"]) for c in cites],
        cited_ids=cited_ids,
    )
