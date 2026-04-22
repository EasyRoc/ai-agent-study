#!/usr/bin/env python3
"""
第 1 周 · 第 1 天：Python 同步对话 + 基本参数 + 三档超时

周计划要求（摘要）：
  - 阅读 chat/completions 的基本参数：model、temperature、max_tokens
  - 实现 chat(message) -> str，并配置 30s / 60s / 120s 三档超时（逐档重试）
  - 记录请求起止时间、返回字符数（token 精确统计可留到后面周次）

运行（在 monorepo-py 目录下）：

  conda activate aimodel
  pip install -r requirements.txt
  cp .env.example .env   # 若尚未配置
  python scripts/week01_day1_sync_chat.py
  python scripts/week01_day1_sync_chat.py "用一句话介绍 Python"
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# openai 底层用 httpx；「读超时」等异常用 httpx 的类型判断，方便做「超时则换下一档」
import httpx

_PY_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(_PY_ROOT / ".env")
    except ImportError:
        pass


def _build_openai_client(*, timeout_seconds: float) -> "object":
    """
    构造 OpenAI 兼容客户端；timeout_seconds 传给 SDK，作为**整次请求**的上限（秒）。
    不同 openai 版本对 timeout 类型略不同，一般 float 即可。
    """
    from openai import OpenAI

    api_key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "请设置环境变量 DASHSCOPE_API_KEY 或 OPENAI_API_KEY（与 health_chat 一致）。"
        )

    base_url = os.environ.get("OPENAI_BASE_URL")
    if not base_url and os.environ.get("DASHSCOPE_API_KEY"):
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if not base_url:
        base_url = "https://api.openai.com/v1"

    # 说明：timeout= 会限制「等待首包+读完全体」的总时间，用于学习「超时」概念；线上要更细粒度可再拆 connect/read
    return OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_seconds)


def chat(
    message: str,
    *,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    timeouts: tuple[float, float, float] = (30.0, 60.0, 120.0),
) -> str:
    """
    同步单轮补全/对话：发一条 user 消息，取 assistant 纯文本。

    参数（对应课程表里的「基本参数」）：
      model         — 模型名；默认与 health_chat 一致（通义 qwen-turbo / 其它 gpt-4o-mini）
      temperature   — 0~2 常见，越大越随机；本练习默认 0.7
      max_tokens    — 回答最多多少 token（由服务端截断；不同厂商叫法可能略不同）
      timeouts      — 三档秒数；某一档**读超时**时自动用下一档重试，**最后一档仍失败**则抛出
    """
    if not message or not message.strip():
        raise ValueError("message 不能为空")

    if model is None:
        model = os.environ.get(
            "LLM_MODEL",
            "qwen-turbo" if os.environ.get("DASHSCOPE_API_KEY") else "gpt-4o-mini",
        )

    # 可重试的「网络层超时」；业务 4xx（如 401）不应靠提高 timeout 解决，应直接失败
    retriable = (
        httpx.ReadTimeout,
        httpx.ConnectTimeout,
        httpx.WriteTimeout,
        httpx.PoolTimeout,
    )

    last_error: Exception | None = None

    for idx, t_sec in enumerate(timeouts, start=1):
        t_wall_start = time.perf_counter()
        client = _build_openai_client(timeout_seconds=t_sec)
        try:
            # create 的 model、temperature、max_tokens 即本日要熟悉的三个核心字段
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message.strip()}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            text = (resp.choices[0].message.content or "").strip()
            elapsed = time.perf_counter() - t_wall_start
            # 计划要求：记录起止与字符数；这里在 stderr 打一行，避免污染「返回值」
            n_chars = len(text)
            rough_tokens = n_chars // 4  # 极粗略，仅作笔记；真实以 API 的 usage 为准
            print(
                f"[第{idx}档 timeout={t_sec:g}s] 总耗时 {elapsed*1000:.1f} ms | "
                f"字符数 {n_chars} | 粗估 token≈{rough_tokens}",
                file=sys.stderr,
            )
            return text
        except retriable as e:
            last_error = e
            print(
                f"[第{idx}档 {t_sec:g}s] 发生可重试超时: {type(e).__name__}: {e!s}",
                file=sys.stderr,
            )
            if idx == len(timeouts):
                break
            print("  → 将使用下一档超时重试…", file=sys.stderr)
        except Exception:
            # 非「读连接超时」类错误：例如 401、内容审核，直接抛给调用方
            raise

    if last_error is not None:
        raise last_error
    raise RuntimeError("未返回结果且无明确异常（逻辑不应到达）")


def _demo() -> int:
    _load_dotenv()
    user_text = "你好"
    if len(sys.argv) >= 2:
        user_text = sys.argv[1]
    try:
        reply = chat(user_text, temperature=1, max_tokens=512)
    except Exception as e:
        print(f"失败: {e}", file=sys.stderr)
        return 1
    print("----- assistant 回复（stdout）-----")
    print(reply)
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
