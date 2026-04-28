"""
通义 compatible-mode：`langchain_openai.ChatOpenAI`（兼容 OpenAI 协议）。

Agent **图编排**仅用 **LangGraph**（见 `react_runner.py`）；本模块不提供也不调用已弃用的 LangChain Agent / Executor API。
"""
from __future__ import annotations

import os

from langchain_openai import ChatOpenAI


def build_chat_model() -> ChatOpenAI:
    key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("AI_DASHSCOPE_API_KEY")
    if not key:
        raise RuntimeError("请设置 DASHSCOPE_API_KEY")
    model = os.environ.get("LLM_MODEL", "qwen-turbo")
    return ChatOpenAI(
        model=model,
        temperature=float(os.environ.get("AGENT_TEMPERATURE", "0.2")),
        api_key=key,
        base_url=os.environ.get("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        timeout=float(os.environ.get("AGENT_LLM_TIMEOUT_SEC", "120")),
    )
