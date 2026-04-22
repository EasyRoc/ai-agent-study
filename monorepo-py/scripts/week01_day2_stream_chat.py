#!/usr/bin/env python3
"""
第 1 周 · 第 2 天：流式输出 + 首 token 时间（TTFT）

周计划要求（摘要）：
  - 实现 stream_chat(messages) -> 生成器，在终端「逐字或逐段」打印
  - 用 time.perf_counter() 记录**第一次 yield 出正文前** 的耗时（首包/首段延迟，自测用）
  - 2～3 行笔记可写在 week01/day2_首token自测.md（运行结束会尝试追加一行数字）

运行（在 monorepo-py 目录下）：

  conda activate aimodel
  python scripts/week01_day2_stream_chat.py
  python scripts/week01_day2_stream_chat.py 用三句话介绍流式输出
"""
from __future__ import annotations

import os
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

_PY_ROOT = Path(__file__).resolve().parent.parent
_NOTES = _PY_ROOT / "week01" / "day2_首token自测.md"


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(_PY_ROOT / ".env")
    except ImportError:
        pass


def _openai_base_config() -> tuple[str, str, str]:
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
        "qwen-turbo" if os.environ.get("DASHSCOPE_API_KEY") else "gpt-4o-mini",
    )
    return api_key, base_url, model


def stream_chat(
    messages: list[dict[str, Any]],
    *,
    model: str | None = None,
    temperature: float = 0.5,
    max_tokens: int = 1024,
    timeout_seconds: float = 120.0,
    metrics: dict[str, float] | None = None,
) -> Iterator[str]:
    """
    流式多轮/单轮：messages 同官方，例如 [{\"role\": \"user\", \"content\": \"你好\"}]。

    - 每收到一小段 assistant 文本就 **yield** 一个 str；终端可 `end=\"\"` + `flush=True` 实现打字机效果。
    - 若传入 `metrics` 非空，会在**第一次出现正文**时写入 `metrics[\"ttft_s\"]`（秒），在生成器**结束**时写入
      `metrics[\"total_s\"]`；便于单元测试，不必解析 stderr。

    TTFT 定义：自「进入 for 循环开始读流」到「第一次 yield 非空正文」的耗时（与课表「第一次 yield 前」一致）。
    """
    if not messages:
        raise ValueError("messages 不能为空")

    from openai import OpenAI

    api_key, base_url, default_model = _openai_base_config()
    if model is None:
        model = default_model

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_seconds)
    t_req = time.perf_counter()
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    first_text = True
    try:
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta is None:
                continue
            text = delta.content
            if not text:
                continue
            if first_text:
                first_text = False
                ttft = time.perf_counter() - t_req
                if metrics is not None:
                    metrics["ttft_s"] = ttft
                print(
                    f"[首段正文/首包延迟 TTFT] 约 {ttft * 1000:.1f} ms",
                    file=sys.stderr,
                )
            yield text
    finally:
        if metrics is not None:
            metrics["total_s"] = time.perf_counter() - t_req


def _append_note_line(ttft_ms: float) -> None:
    _NOTES.parent.mkdir(parents=True, exist_ok=True)
    line = f"- {time.strftime('%Y-%m-%d %H:%M:%S')}  TTFT 约 {ttft_ms:.0f} ms\n"
    if not _NOTES.exists():
        _NOTES.write_text(
            "# 第 1 周第 2 天：首 token 自测\n\n"
            "下面为每次运行**自动追加**的一行；请再**手写** 1～2 行：当时用的**模型名**、网络（家宽/公司）即可。\n\n"
            + line,
            encoding="utf-8",
        )
    else:
        with _NOTES.open("a", encoding="utf-8") as f:
            f.write(line)


def _main() -> int:
    _load_dotenv()
    user_line = "什么是大模型的流式输出？"
    if len(sys.argv) >= 2:
        user_line = " ".join(sys.argv[1:])

    messages: list[dict[str, Any]] = [{"role": "user", "content": user_line.strip()}]
    m: dict[str, float] = {}

    print("（stderr）以下为模型**流式**输出；正文在 stdout 连续打印。\n", file=sys.stderr)
    for piece in stream_chat(
        messages, temperature=0.4, max_tokens=800, timeout_seconds=120.0, metrics=m
    ):
        print(piece, end="", flush=True)
    print()

    if "ttft_s" in m:
        _append_note_line(m["ttft_s"] * 1000.0)
        print(
            f"（stderr）已把约 {m['ttft_s']*1000:.0f} ms 追加到: {_NOTES.relative_to(_PY_ROOT)}",
            file=sys.stderr,
        )
    if "total_s" in m:
        print(
            f"（stderr）从发起流到结束约 {m['total_s']*1000:.1f} ms",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except Exception as e:
        print(f"失败: {e}", file=sys.stderr)
        raise SystemExit(1)
