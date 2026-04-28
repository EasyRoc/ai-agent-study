"""
第 6 周对照组：多步 **Function Calling**（非 LangGraph 图）——`bind_tools` + 执行 `tool_calls` 续写。

ReAct 路线请用 `react_runner`（**LangGraph** `create_react_agent`）。与「只 prompt 的假 ReAct」差异见 `notes/fc-notes.md`。
"""
from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from week06.llm_factory import build_chat_model
from week06.tools import default_tools

logger = logging.getLogger(__name__)


def run_fc_loop(user_text: str, *, max_rounds: int = 5) -> tuple[str, list[dict[str, Any]]]:
    tools = default_tools()
    by_name = {str(t.name): t for t in tools}
    llm = build_chat_model().bind_tools(tools)
    messages: list[Any] = [HumanMessage(content=user_text.strip())]
    journal: list[dict[str, Any]] = []

    for _ in range(max_rounds):
        ai: AIMessage = llm.invoke(messages)
        messages.append(ai)
        tcs = getattr(ai, "tool_calls", None) or []
        if not tcs:
            txt = str(ai.content or "").strip()
            journal.append({"phase": "assistant_final", "text_preview": txt[:500]})
            return txt, journal
        journal.append(
            {
                "phase": "ai_tool_calls",
                "calls": [
                    {"name": c.get("name"), "args": c.get("args", c.get("arguments", {}))}
                    for c in tcs
                ],
            }
        )
        for tc in tcs:
            name = str(tc.get("name", ""))
            args = tc.get("args") or tc.get("arguments") or {}
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}
            fn = by_name.get(name)
            try:
                if fn is None:
                    out = json.dumps({"error": f"未知工具 {name}"}, ensure_ascii=False)
                else:
                    out = fn.invoke(args)
            except Exception as e:
                logger.exception("tool %s", name)
                out = json.dumps({"error": str(e)[:500]}, ensure_ascii=False)
            tid = str(tc.get("id") or name)
            messages.append(ToolMessage(content=str(out), tool_call_id=tid, name=name))
            journal.append(
                {"phase": "tool_result", "name": name, "content_preview": str(out)[:500]}
            )

    return (
        json.dumps(
            {"note": f"已达 max_rounds={max_rounds}", "hint": "可调大 max_rounds 或检查模型是否停不下工具循环"},
            ensure_ascii=False,
        ),
        journal,
    )
