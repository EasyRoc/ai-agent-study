"""第 6 周：FastAPI `POST /agent/fc` 与 `/agent/react`，供联调与录制轨迹。"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from week06.fc_loop import run_fc_loop
from week06.react_runner import append_trace_log, run_react_agent
from week06.tools import content_filter_block

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["week06-agent"])
_ROOT = Path(__file__).resolve().parent.parent
_TRACE = _ROOT / "notes" / "react-trace.log"


def _load_env() -> None:
    p = _ROOT / ".env"
    load_dotenv(p if p.is_file() else None)


class AgentRunBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt: str = Field(..., min_length=1, description="用户多意图自然语言")
    max_steps: int = Field(5, ge=1, le=12, alias="maxSteps", description="FC 轮次 / ReAct 递归参考")
    write_trace: bool = Field(True, alias="writeTrace", description="是否追加 notes/react-trace.log")


class AgentRunResponse(BaseModel):
    answer: str
    mode: str
    journal: list | None = None


@router.post("/fc", response_model=AgentRunResponse)
def run_fc(body: AgentRunBody) -> AgentRunResponse:
    _load_env()
    g = content_filter_block(body.prompt)
    if g:
        return AgentRunResponse(answer=g, mode="fc", journal=None)
    ans, journal = run_fc_loop(body.prompt, max_rounds=body.max_steps)
    if body.write_trace:
        try:
            append_trace_log(str(_TRACE), body.prompt, journal or [], ans)
        except OSError:
            logger.warning("无法写入 react-trace.log")
    return AgentRunResponse(answer=ans, mode="fc", journal=journal)


@router.post("/react", response_model=AgentRunResponse)
def run_react(body: AgentRunBody) -> AgentRunResponse:
    _load_env()
    g = content_filter_block(body.prompt)
    if g:
        return AgentRunResponse(answer=g, mode="react", journal=None)
    ans, trace = run_react_agent(body.prompt, max_steps=body.max_steps)
    if body.write_trace:
        try:
            append_trace_log(str(_TRACE), body.prompt, trace, ans)
        except OSError:
            logger.warning("无法写入 react-trace.log")
    return AgentRunResponse(answer=ans, mode="react", journal=trace)
