#!/usr/bin/env python3
"""
第 1 周 · Function Calling 最小闭环（与周计划「tools 选做」一致）

流程：第一次请求带 tools → 若返回 tool_calls → 本地执行 → 把 assistant + tool 消息拼进 messages →
第二次请求直到得到纯文本终答（无 tool_calls）。

运行（在 monorepo-py 目录下）：

  conda activate aimodel
  python scripts/fc_min.py
  python scripts/fc_min.py "算一下 11 加 22 等于多少"
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

_PY_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(_PY_ROOT / ".env")
    except ImportError:
        pass


def _openai_client(*, timeout_seconds: float = 120.0) -> Any:
    from openai import OpenAI

    api_key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("请设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY。")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not base_url and os.environ.get("DASHSCOPE_API_KEY"):
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if not base_url:
        base_url = "https://api.openai.com/v1"
    model = os.environ.get(
        "LLM_MODEL",
        "qwen-plus" if os.environ.get("DASHSCOPE_API_KEY") else "gpt-4o-mini",
    )
    return OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_seconds), model


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "计算两个实数之和",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个加数"},
                    "b": {"type": "number", "description": "第二个加数"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "server_time_iso",
            "description": "返回本机当前时间的 ISO-8601 字符串，可选时区名如 Asia/Shanghai",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA 时区，如 Asia/Shanghai；缺省为本地时区",
                    }
                },
                "required": [],
            },
        },
    },
]


def _run_tool(name: str, arguments_json: str) -> str:
    args = json.loads(arguments_json) if arguments_json else {}
    if name == "add_numbers":
        a = float(args["a"])
        b = float(args["b"])
        return str(a + b)
    if name == "server_time_iso":
        from datetime import datetime
        from zoneinfo import ZoneInfo

        tz_name = (args.get("timezone") or "").strip()
        if tz_name:
            dt = datetime.now(ZoneInfo(tz_name))
        else:
            dt = datetime.now().astimezone()
        return dt.isoformat(timespec="seconds")
    return f"未知工具: {name}"


def chat_with_tools(
    user_text: str,
    *,
    max_rounds: int = 5,
    temperature: float = 0.2,
) -> str:
    """
    多轮：直到 assistant 无 tool_calls 或达到 max_rounds。
    第二次及以后请求体里的 messages 会包含：原 user、含 tool_calls 的 assistant、role=tool 的若干条等。
    """
    client, model = _openai_client()
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_text.strip()}]

    for _round in range(max_rounds):
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=temperature,
        )
        choice = resp.choices[0]
        msg = choice.message
        if not msg.tool_calls:
            return (msg.content or "").strip()

        # 必须把带 tool_calls 的 assistant 原样写回（第二次请求前拼进 history）
        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments or "{}",
                        },
                    }
                    for tc in msg.tool_calls
                ],
            }
        )
        for tc in msg.tool_calls:
            out = _run_tool(tc.function.name, tc.function.arguments or "{}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": out,
                }
            )

    raise RuntimeError(f"超过 max_rounds={max_rounds} 仍未得到终答（请检查工具或换模型）")


def _main() -> int:
    _load_dotenv()
    line = "现在几点了？用工具回答当前时间的 ISO 字符串。若问数字，可调用 add_numbers。"
    if len(sys.argv) >= 2:
        line = " ".join(sys.argv[1:])
    try:
        answer = chat_with_tools(line)
        print(answer)
    except Exception as e:
        print(f"失败: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
