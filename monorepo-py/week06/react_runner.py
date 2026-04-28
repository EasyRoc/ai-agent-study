"""
第 6 周：LangGraph `create_react_agent`；`recursion_limit` 控制最大循环步数（打满时可见截断说明）。
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from week06.llm_factory import build_chat_model
from week06.tools import default_tools

logger = logging.getLogger(__name__)


def _summarize_message(m: Any) -> dict[str, Any]:
    t = type(m).__name__
    if isinstance(m, HumanMessage):
        return {"type": "human", "content_preview": str(m.content)[:200]}
    if isinstance(m, AIMessage):
        tc = getattr(m, "tool_calls", None) or []
        calls = []
        if isinstance(tc, list):
            for x in tc:
                if isinstance(x, dict):
                    calls.append(
                        {
                            "name": x.get("name"),
                            "args_preview": str(x.get("args", {}))[:160],
                        }
                    )
        return {
            "type": "ai",
            "content_preview": (str(m.content)[:300] if m.content else ""),
            "tool_calls": calls,
        }
    if isinstance(m, ToolMessage):
        return {
            "type": "tool_result",
            "name": getattr(m, "name", ""),
            "content_preview": str(m.content)[:400],
        }
    return {"type": t, "preview": str(m)[:200]}


def run_react_agent(user_text: str, *, max_steps: int = 5) -> tuple[str, list[dict[str, Any]]]:
    from langgraph.errors import GraphRecursionError

    from langgraph.prebuilt import create_react_agent

    llm = build_chat_model()
    tools = default_tools()
    graph = create_react_agent(llm, tools)
    # 一步 ≈ model + 可选 tool；上限给紧一点便于课程验收「打满截断」日志
    recursion_limit = max(6, min(int(os.environ.get("AGENT_RECURSION_LIMIT", str(max_steps * 3 + 6))), 80))
    cfg = {"recursion_limit": recursion_limit}
    trace: list[dict[str, Any]] = []
    try:
        final = graph.invoke(
            {"messages": [HumanMessage(content=user_text.strip())]},
            config=cfg,
        )
    except GraphRecursionError:
        err = json.dumps(
            {
                "note": "已达到 max_steps / recursion_limit 上限",
                "max_steps_param": max_steps,
                "recursion_limit": recursion_limit,
            },
            ensure_ascii=False,
        )
        trace.append({"type": "system", "event": "GraphRecursionError"})
        return err, trace
    except Exception as e:
        logger.exception("ReAct invoke 失败")
        return json.dumps({"error": str(e)[:800]}, ensure_ascii=False), [{"type": "error", "detail": str(e)[:200]}]

    msgs = final.get("messages", [])
    trace = [_summarize_message(m) for m in msgs]
    final_text = ""
    for m in reversed(msgs):
        if isinstance(m, AIMessage) and (m.content or "").strip():
            final_text = str(m.content).strip()
            break
    if not final_text:
        final_text = json.dumps(
            {"note": "未解析到最终 assistant 文本；请见 trace 中 tool_result", "truncated": False},
            ensure_ascii=False,
        )
    return final_text, trace


def append_trace_log(path: str, user_text: str, trace: list[dict[str, Any]], final_text: str) -> None:
    from pathlib import Path

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    block = (
        "\n---\n"
        f"user: {user_text[:500]!r}\n"
        f"steps: {json.dumps(trace, ensure_ascii=False, indent=2)}\n"
        f"final: {final_text[:2000]!r}\n"
    )
    with p.open("a", encoding="utf-8") as f:
        f.write(block)
