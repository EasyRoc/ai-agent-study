#!/usr/bin/env python3
"""
第 2 周：两版 system prompt + LangChain with_structured_output，跑同一输入各 5 次，观察成功率与延迟。
通义/灵积：使用 OpenAI 兼容端点 + DASHSCOPE_API_KEY（与第 0～1 周一致）。
"""
from __future__ import annotations

import os
import statistics
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


def _load_dotenv() -> None:
    for d in (Path(__file__).resolve().parents[1], Path.cwd()):
        p = d / ".env"
        if p.is_file():
            load_dotenv(p)
            return
    load_dotenv()


class IntentSlots(BaseModel):
    """强类型输出契约，相当于 Java 的 record/DTO；LangChain 会据此生成 JSON Schema 并解析模型输出。"""

    intent: str = Field(description="用户意图，英文 snake_case")
    slots: dict[str, str] = Field(default_factory=dict, description="槽位，键值均为短字符串")


SYSTEM_V1 = """你是意图与槽位抽取器。只输出可解析的 JSON 思路由框架处理；用户会输入中文说法。
约定字段：intent（snake_case）、slots（键值字符串）。"""

SYSTEM_V2 = """你是意图与槽位抽取器。只根据用户说法抽取 intent 与 slots。
示例：
用户说「订明天下午三点的会议室」 → intent=book_meeting_room，slots 含 date、time
用户说「查报销」 → intent=query_reimbursement，slots 可为空
不要输出除结构化结果外的长解释。"""


def _build_llm() -> ChatOpenAI:
    key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("AI_DASHSCOPE_API_KEY")
    if not key:
        print("请设置 DASHSCOPE_API_KEY", file=sys.stderr)
        sys.exit(2)
    model = os.environ.get("LLM_MODEL", "qwen-turbo")
    return ChatOpenAI(
        model=model,
        temperature=0.2,
        api_key=key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=120.0,
    )


def _run_batch(
    llm, system: str, user: str, n: int = 5
) -> tuple[int, list[float], str | None, IntentSlots | None]:
    """同一 system + user 重复调用 n 次，统计成功次数、耗时，并保留「最后一次成功」的 IntentSlots。

    与 Java 的对照：with_structured_output(IntentSlots) ≈ Spring AI ChatClient 的 .entity(Dto.class)，
    invoke 成功时返回已解析的强类型对象。
    """
    # include_raw=False：不要额外返回「原始模型字符串」，只要解析后的 IntentSlots
    chain = llm.with_structured_output(IntentSlots, include_raw=False)
    times: list[float] = []
    ok = 0
    last_err: str | None = None
    last_structured: IntentSlots | None = None
    for i in range(n):
        t0 = time.perf_counter()
        try:
            result = chain.invoke(
                [SystemMessage(content=system), HumanMessage(content=user)]
            )
            ok += 1
            if isinstance(result, IntentSlots):
                last_structured = result
            else:
                last_structured = IntentSlots.model_validate(result)
        except Exception as e:  # noqa: BLE001 — 课表要求记录失败样例
            # 解析失败或 API 错误会进这里（类似 entity 反序列化失败）
            last_err = f"{type(e).__name__}: {e}"
        times.append(time.perf_counter() - t0)
    return ok, times, last_err, last_structured


def main() -> int:
    _load_dotenv()
    user_text = (sys.argv[1] if len(sys.argv) > 1 else "帮我订周一下午两点的会议").strip()
    llm = _build_llm()
    print(f"输入: {user_text!r}\n")

    for name, system in (("v1", SYSTEM_V1), ("v2", SYSTEM_V2)):
        ok, times, err, last_parsed = _run_batch(llm, system, user_text, 5)
        avg = statistics.mean(times) * 1000.0
        print(f"=== {name} ===")
        print(f"  成功 {ok}/5  |  平均延迟 {avg:.0f} ms")
        if err and ok < 5:
            print(f"  末次错误样例: {err}")
        if last_parsed is not None:
            # 打印 n 次里「最后一次成功」的结构化结果（Pydantic v2：model_dump 即 dict，便于对照 Java DTO）
            print("  结构化结果（最后一次成功，JSON）:")
            print(
                "  "
                + last_parsed.model_dump_json(indent=2, ensure_ascii=False).replace(
                    "\n", "\n  "
                )
            )
        else:
            print("  结构化结果: 无（本组全部失败）")
        print()

    notes = Path(__file__).resolve().parents[1] / "notes" / "failures.md"
    if not notes.exists():
        notes.parent.mkdir(parents=True, exist_ok=True)
        notes.write_text(
            "# 第 2 周：解析失败样例\n\n"
            "（由 week02 脚本在首次运行时可生成；你可手工补充 3 条错例+改法。）\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
