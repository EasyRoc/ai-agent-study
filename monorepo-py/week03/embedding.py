"""通义/灵积 text-embedding 兼容端点，与第 0～1 周 DASHSCOPE_API_KEY 一致。"""

# 让类型注解里可以先写「尚未在本文件定义的」类名（和 Java 里部分泛型/前向引用场景类似）
from __future__ import annotations

import os

# LangChain：用「OpenAIEmbeddings」去调任何 OpenAI-兼容的 HTTP 服务，本仓把 base_url 指到通义灵积
from langchain_openai import OpenAIEmbeddings


def build_dashscope_embeddings() -> OpenAIEmbeddings:
    # `os.environ` 类似 `System.getenv`；`a or b`：若 a 为 None/空串/假值则取 b（常见「默认值」惯用法）
    key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("AI_DASHSCOPE_API_KEY")
    if not key:
        msg = "请设置 DASHSCOPE_API_KEY 或 AI_DASHSCOPE_API_KEY"
        raise RuntimeError(msg)
    # 与 DashScope 兼容 OpenAPI 的 embedding 名称以官方为准；见 README 中维度说明
    model = os.environ.get("EMBEDDING_MODEL", "text-embedding-v2")
    # 返回一个「能 embed 文本」的对象，后面 ingest/api 会复用（Java 里类似注入一个 Client Bean）
    return OpenAIEmbeddings(
        model=model,
        openai_api_key=key,
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        check_embedding_ctx_length=False,
    )


def embed_dim_one_sample(embeddings: OpenAIEmbeddings) -> int:
    """对短句做一次嵌入，得到向量维数（用于 /embed 与日志）。"""
    v = embeddings.embed_query("维数探测")
    # `len(v)`：向量维数，v 在运行时是 `list[float]`，可脑补成可生长的 float 数组
    return len(v)
