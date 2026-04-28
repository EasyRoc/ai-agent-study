"""
第 6 周：供 LangGraph / FC 使用的工具定义。

- **Agent 编排**：见 `react_runner.py`（`langgraph.prebuilt.create_react_agent`）与 `fc_loop.py`（手写 FC 闭环对照），**不**使用已弃用的 `langchain.agents` / `AgentExecutor`。
- **工具装饰器**：`langchain_core.tools.tool` 与 LangGraph 官方文档及 `ChatOpenAI.bind_tools` 的集成方式一致；消息类型使用 `langchain_core.messages` 仅为与上述模型接口对齐。
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def knowledge_search(query: str) -> str:
    """在公司制度语料中检索与「请假、报销、考勤、福利」等相关的文本片段。参数 query 用中文关键词或短句。"""
    q = (query or "").strip()
    if not q:
        return json.dumps({"error": "query 为空"}, ensure_ascii=False)
    try:
        from week05.hybrid import hybrid_search

        pairs = hybrid_search(q, k_vec=12, k_kw=12, k_out=5)
        if not pairs:
            return json.dumps({"hits": [], "note": "无检索结果"}, ensure_ascii=False)
        hits = []
        for p in pairs:
            hits.append({"id": p.id, "text": (p.text or "")[:500]})
        return json.dumps({"hits": hits}, ensure_ascii=False)
    except Exception as e:
        logger.exception("knowledge_search 失败")
        return json.dumps({"error": str(e)[:500]}, ensure_ascii=False)


@tool
def get_weather(city: str) -> str:
    """查询城市天气（演示用 mock API，非真实气象数据）。参数 city 为城市中文名或拼音。"""
    c = (city or "").strip() or "未知"
    return json.dumps(
        {"city": c, "condition": "晴", "temp_c": 26, "mock": True},
        ensure_ascii=False,
    )


@tool
def add_numbers(a: float, b: float) -> str:
    """计算两个数之和；用于多意图题里「顺便算一下」类子问题。"""
    try:
        return json.dumps({"result": float(a) + float(b)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def default_tools() -> list[Any]:
    return [knowledge_search, get_weather, add_numbers]


_SENSITIVE = re.compile(r"(赌|毒|枪|恐袭|制作炸药)", re.I)


def content_filter_block(user_text: str) -> str | None:
    """明显敏感则拒绝走工具；返回错误提示内容，或 None 表示放行。"""
    if not user_text or not user_text.strip():
        return "请输入有效问题。"
    if _SENSITIVE.search(user_text):
        return "该问题涉及敏感内容，已拒绝调用工具与外部接口。"
    return None
