"""
第 3 周：FastAPI 提供 POST /search、POST /embed；依赖 Milvus 中已入库的 collection（先运行 week03.ingest）。

启动（默认端口 8010，与 java-demo 中 app.vector.base-url 一致）：

  cd monorepo-py && python -m uvicorn week03.api:app --host 0.0.0.0 --port 8010
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path


def _configure_app_logging() -> None:
    """
    仅对业务包加 Handler，不调用 basicConfig(force=True) 以免冲掉 Uvicorn 的访问/错误日志。

    环境变量 LOG_LEVEL 默认 INFO；子 logger（如 week04.rag_service）会向上冒泡到 week04。
    """
    name = (os.environ.get("LOG_LEVEL") or "INFO").strip().upper()
    level = getattr(logging, name, logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    for ns in ("week04", "week05", "week06", "week03"):
        lg = logging.getLogger(ns)
        lg.setLevel(level)
        if lg.handlers:
            continue
        h = logging.StreamHandler(sys.stderr)
        h.setLevel(level)
        h.setFormatter(fmt)
        lg.addHandler(h)
        lg.propagate = False


_configure_app_logging()

from dotenv import load_dotenv
# FastAPI ≈ 轻量 Web 框架，声明式路由 + 自动 OpenAPI，习惯上可对照 Spring WebFlux/MVC 的 @RestController
from fastapi import FastAPI
# Pydantic BaseModel：请求/响应体校验 + 序列化，和 Bean Validation + Jackson DTO 常一起用那套有点像
from pydantic import BaseModel, Field
from langchain_milvus import Milvus

from week03.milvus_settings import (
    COLLECTION_NAME,
    connection_args,
    connection_summary,
    ensure_milvus_lite_for_local_db,
    prime_orm_connection_before_langchain_milvus,
    register_orm_connection_for_langchain_milvus,
    server_and_collection_ok,
)
from week04.rag_api import router as _rag_router
from week05.rag_task_api import router as _rag_tasks_router
from week06.agent_api import router as _week06_agent_router

_ROOT = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)

# 模块级单例：uvicorn 会加载本模块的 `app`，类似 Spring 里拿 ApplicationContext 上挂的那个主 Bean
app = FastAPI(
    title="aimodel-week03-06",
    description="L2 /search；RAG /rag/tasks；第6周 Agent /agent/fc /agent/react",
    version="0.4.0",
)


def _load_dotenv() -> None:
    p = _ROOT / ".env"
    if p.is_file():
        load_dotenv(p)
    else:
        load_dotenv()


def _vectorstore() -> Milvus:
    # 晚加载 embedding 工厂：和 ingest 里一样，少一次「一 import 就要求密钥已配置」
    from week03.embedding import build_dashscope_embeddings

    _load_dotenv()
    ensure_milvus_lite_for_local_db()
    emb = build_dashscope_embeddings()
    # 若集合已存在，LangChain 在 Milvus() 的 __init__ 里会立刻访问 ORM Collection，须先 connect（见 milvus_settings.prime_…）
    prime_orm_connection_before_langchain_milvus()
    # 读接口这里 drop_old 必须为 False，否则会每次请求删库，只连已有 collection
    store = Milvus(
        embedding_function=emb,
        collection_name=COLLECTION_NAME,
        connection_args=connection_args(),
        drop_old=False,
        auto_id=False,
    )
    register_orm_connection_for_langchain_milvus(store)
    return store


class SearchBody(BaseModel):
    # Field(...) 里 `...` 表示必传，类似 @NotNull；不设 default 的字段在 Pydantic v2 里也是必传
    q: str = Field(..., min_length=1, description="查询文本")
    k: int = Field(3, ge=1, le=20, description="Top-K")


class SearchHit(BaseModel):
    id: str
    text: str
    score: float = Field(..., description="相似度，越大越相似（由距离换算）")


class SearchResponse(BaseModel):
    results: list[SearchHit]
    model: str
    memory_layer: str = "L2_retrieval"


class EmbedBody(BaseModel):
    text: str = Field(..., min_length=1)


class EmbedResponse(BaseModel):
    model: str
    dimension: int


# `@app.get` / `@app.post` 类似 `@GetMapping` `@PostMapping`；下面函数的参数类型用了 Pydantic 时 FastAPI 会帮你从 JSON 体反序列化
@app.get("/health")
def health() -> dict:
    ok, has_col = server_and_collection_ok()
    return {
        "ok": bool(ok and has_col),
        "milvus": connection_summary(),
        "collection": COLLECTION_NAME,
        "ingested": bool(has_col),
    }


@app.post("/search", response_model=SearchResponse)
def search(body: SearchBody) -> SearchResponse:
    model = os.environ.get("EMBEDDING_MODEL", "text-embedding-v2")
    # 课表：库坏了/没 ingest 也返回 200 + 空 results，不抛 500（和 GlobalException 里「别吓调用方」一致）
    # 调试：若 results 总为空，请看终端里 logger.exception 栈；或设 os.environ["WEEK03_SEARCH_RAISE"]="1" 让异常直接抛出
    _raise = os.environ.get("WEEK03_SEARCH_RAISE", "").strip().lower() in ("1", "true", "yes")
    try:
        vs = _vectorstore()
    except Exception:
        logger.exception("week03 /search: _vectorstore() 失败（仍返回空 results 以符合课表）")
        if _raise:
            raise
        return SearchResponse(results=[], model=model)
    try:
        # 返回 (Document, 距离) 列表；L2 下 dist 越小越近，下面再映射成「越大越像」
        pairs = vs.similarity_search_with_score(body.q, k=body.k)
    except Exception:
        logger.exception("week03 /search: similarity_search_with_score 失败（仍返回空 results）")
        if _raise:
            raise
        return SearchResponse(results=[], model=model)
    if not pairs:
        logger.warning(
            "week03 /search: 检索 0 条（库空、未 load、或 query 与索引无交集）。q=%r k=%s",
            body.q,
            body.k,
        )
    out: list[SearchHit] = []
    for doc, dist in pairs:
        meta = doc.metadata or {}
        # 动态取属性：Java 要反射，Python 里 getattr(对象, "属性名", 缺省)
        did = getattr(doc, "id", None)
        cid = (
            meta.get("id")
            or meta.get("pk")
            or (str(did) if did is not None else f"row-{len(out)}")
        )
        # 与 Chroma 时代一致的一阶映射，便于人眼比较 score；不是严格的概率
        score = float(1.0 / (1.0 + float(dist)))
        out.append(SearchHit(id=str(cid), text=doc.page_content, score=score))
    return SearchResponse(results=out, model=model)


@app.post("/embed", response_model=EmbedResponse)
def embed_one(body: EmbedBody) -> EmbedResponse:
    from week03.embedding import build_dashscope_embeddings

    _load_dotenv()
    emb = build_dashscope_embeddings()
    vec = emb.embed_query(body.text)
    m = os.environ.get("EMBEDDING_MODEL", "text-embedding-v2")
    return EmbedResponse(model=m, dimension=len(vec))


# 第 4 周：/rag/ask 与 week03 共用进程与端口
app.include_router(_rag_router)
# 第 5 周：长 RAG 任务 202 形态（内存轮询，演示用）
app.include_router(_rag_tasks_router)
app.include_router(_week06_agent_router)
