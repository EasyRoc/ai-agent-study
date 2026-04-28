"""
第 5 周「长任务」示意：202 Accepted + taskId，内存轮询 `GET`（多 worker 不共享，生产需 Redis/队列）。

设计文档与 Kafka 长什么样见仓库 `docs/week05-long-task-kafka.md`。
"""
from __future__ import annotations

import logging
import threading
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from week04.rag_service import run_rag

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag/tasks", tags=["week05-rag-tasks"])


def _load_dotenv() -> None:
    from pathlib import Path
    from dotenv import load_dotenv

    p = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(p if p.is_file() else None)


class RagTaskCreateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    question: str = Field(..., min_length=1)
    top_k: int = Field(4, ge=1, le=10, alias="topK", description="与 /rag/ask 一致，服务端会钳制")
    session_id: str | None = Field(None, alias="sessionId", description="可选")


class RagTaskCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(..., alias="taskId", serialization_alias="taskId")
    status: str = "pending"


class RagTaskGetResponse(BaseModel):
    status: str
    answer: str | None = None
    error: str | None = None


_lock = threading.Lock()
_tasks: dict[str, dict[str, Any]] = {}


def _run_in_bg(tid: str, body: RagTaskCreateBody) -> None:
    def _w() -> None:
        _load_dotenv()
        time.sleep(0)  # 让 202 先飞回客户端
        try:
            top_k = max(1, min(10, body.top_k))
            ans, _c, _d = run_rag(body.question, top_k=top_k, session_id=body.session_id)
            with _lock:
                t = _tasks.get(tid)
                if t is not None:
                    t["status"] = "done"
                    t["answer"] = ans
        except Exception as e:
            logger.exception("RAG 后台任务失败 tid=%s", tid)
            with _lock:
                t = _tasks.get(tid)
                if t is not None:
                    t["status"] = "error"
                    t["error"] = str(e)[:2000]

    threading.Thread(target=_w, name=f"rag-task-{tid}", daemon=True).start()


@router.post("", response_model=None)
def create_rag_task(body: RagTaskCreateBody) -> Any:
    _load_dotenv()
    from fastapi.responses import JSONResponse

    tid = str(uuid.uuid4())
    with _lock:
        _tasks[tid] = {"status": "pending", "t": time.time(), "question": body.question}
    _run_in_bg(tid, body)
    return JSONResponse(
        status_code=202,
        content=RagTaskCreateResponse(task_id=tid, status="pending").model_dump(by_alias=True),
        headers={"Location": f"/rag/tasks/{tid}"},
    )


@router.get("/{task_id}", response_model=RagTaskGetResponse)
def get_rag_task(task_id: str) -> RagTaskGetResponse:
    with _lock:
        t = _tasks.get(task_id)
    if not t:
        raise HTTPException(404, "task 不存在或已过期")
    st = t.get("status", "pending")
    if st == "done":
        return RagTaskGetResponse(status="done", answer=str(t.get("answer", "")))
    if st == "error":
        return RagTaskGetResponse(status="error", error=t.get("error", ""))
    return RagTaskGetResponse(status=st)
