"""
L0 短期记忆（多轮 RAG，与 L2 向量知识库解耦）：

- 以 sessionId 为 key，在**本进程**内保存最近若干轮「用户 / 助手」原文摘要；
- 只注入 LLM 提示，**不**写入 Milvus、不参与向量检索；
- 多 worker / 多机需自行换 Redis 等，环境变量名沿用便于迁移。
"""
from __future__ import annotations

import os
import threading
from collections import deque

_lock = threading.RLock()
# session_id -> 最近 N 轮 (user, assistant)
_store: dict[str, deque[tuple[str, str]]] = {}


def _max_turns() -> int:
    try:
        v = int(os.environ.get("RAG_SESSION_MAX_TURNS", "5"))
    except ValueError:
        v = 5
    return max(1, min(20, v))


def _user_max_chars() -> int:
    try:
        v = int(os.environ.get("RAG_SESSION_USER_MAX_CHARS", "500"))
    except ValueError:
        v = 500
    return max(50, min(2000, v))


def _answer_max_chars() -> int:
    try:
        v = int(os.environ.get("RAG_SESSION_ANSWER_PREVIEW_CHARS", "500"))
    except ValueError:
        v = 500
    return max(100, min(2000, v))


def _enabled() -> bool:
    return os.environ.get("RAG_SESSION_MEMORY_ENABLED", "true").lower() in ("1", "true", "yes", "on")


def get_history_for_prompt(session_id: str | None) -> str:
    """无 session 或关闭记忆时返回空串。"""
    if not _enabled() or not session_id:
        return ""
    sid = str(session_id).strip()
    if not sid:
        return ""
    with _lock:
        turns = _store.get(sid)
        if not turns:
            return ""
        copy = list(turns)
    lines: list[str] = [
        "【近期对话（L0 短期记忆，仅帮助理解多轮指代与语境；"
        "制度、数字、条款**必须以**下方【参考资料】为准，不得把本段当事实来源）】"
    ]
    ulim, alim = _user_max_chars(), _answer_max_chars()
    for u, a in copy:
        u1 = (u or "").replace("\n", " ").strip()[:ulim]
        a1 = (a or "").replace("\n", " ").strip()[:alim]
        if u1:
            lines.append(f"用户：{u1}")
        if a1:
            lines.append(f"助手：{a1}")
        lines.append("")
    return "\n".join(lines) + "\n"


def append_turn(session_id: str | None, user: str, assistant: str) -> None:
    """追加一轮；无 session 或关闭时 no-op。用户问题为空时不记录。"""
    if not _enabled() or not session_id:
        return
    sid = str(session_id).strip()
    if not sid:
        return
    u = (user or "").strip()
    a = (assistant or "").strip()
    if not u:
        return
    with _lock:
        if sid not in _store:
            _store[sid] = deque(maxlen=_max_turns())
        _store[sid].append((u, a))
