#!/usr/bin/env python3
"""
第 3 周：读 data/corpus.txt，按行建文档、走 RecursiveCharacterTextSplitter（对超长行可再切分）、写入 Milvus（LangChain Milvus 向量库）。

用法：在 monorepo-py 下执行
  python -m week03.ingest
需已配置 DASHSCOPE_API_KEY；可选 EMBEDDING_MODEL（默认 text-embedding-v2）。

Milvus 连接见 week03/milvus_settings.py（默认同目录下 data/milvus_lite.db 的 Milvus Lite）。
"""
from __future__ import annotations

import os
import sys
# 运行方式：`python -m week03.ingest`（模块方式）比改 PYTHONPATH 更省心，类似 `java -p … -m com.x.Main`
from pathlib import Path

from dotenv import load_dotenv
# Document ≈ 一条可检索记录：page_content=正文，metadata=附加字段（和 Map<String,Object> 类似）
from langchain_core.documents import Document
from langchain_milvus import Milvus
from week03.corpus_chunks import build_corpus_documents, corpus_path
from week03.milvus_settings import (
    COLLECTION_NAME,
    connection_args,
    connection_summary,
    ensure_milvus_lite_for_local_db,
    prime_orm_connection_before_langchain_milvus,
    register_orm_connection_for_langchain_milvus,
)

_ROOT = Path(__file__).resolve().parent.parent
_CORPUS = corpus_path()


def _load_dotenv() -> None:
    # 与 Java 的 dotenv/ Spring @PropertySource 类似：从 .env 文件灌进 os.environ
    p = _ROOT / ".env"
    if p.is_file():
        load_dotenv(p)
    else:
        load_dotenv()


def main() -> int:
    _load_dotenv()
    # 在真正 new Milvus 前先检查 milvus_lite 是否可导入（与官方 MilvusClient("./x.db") 要求一致）
    ensure_milvus_lite_for_local_db()
    if not _CORPUS.is_file():
        print(f"缺少语料: {_CORPUS}", file=sys.stderr)
        return 1
    # 放函数体里再 import，避免 `python -m week03` 的某些场景下未配置密钥就加载模块时立刻报错
    from week03.embedding import build_dashscope_embeddings, embed_dim_one_sample

    emb = build_dashscope_embeddings()
    dim = embed_dim_one_sample(emb)
    print(f"Embedding 模型: {os.environ.get('EMBEDDING_MODEL', 'text-embedding-v2')}  维数: {dim}")

    docs = build_corpus_documents()
    # 与 Milvus 主键一一对应；auto_id=False 时必须在 add_documents 里显式传 ids
    ids = [f"chunk-{i}" for i in range(len(docs))]
    for i, doc in enumerate(docs):
        # `x or {}`：metadata 为 None 时换空 dict，和 Optional.map 的防御式写法一个意思
        m = dict(doc.metadata or {})
        m["id"] = ids[i]
        doc.metadata = m

    conn = connection_args()
    # 若本机已有 week03_hr，__init__ 会立刻用 ORM；与 api 同逻辑，先 prime
    prime_orm_connection_before_langchain_milvus()
    # LangChain 的 VectorStore 封装；drop_old=True 会删旧 collection 再建（幂等、可复现数据）
    store = Milvus(
        embedding_function=emb,
        collection_name=COLLECTION_NAME,
        connection_args=conn,
        drop_old=True,
        auto_id=False,
    )
    # 否则 add_documents → ORM Collection 时抛「should create connection first」，见 milvus_settings
    register_orm_connection_for_langchain_milvus(store)
    store.add_documents(docs, ids=ids)
    print(
        f"已写入 {len(docs)} 条到 Milvus（collection={COLLECTION_NAME}，{connection_summary()}）"
        "，L2 外显/检索记忆，与 L0 会话分桶。"
    )
    return 0


# 直接运行本文件时进 main()；被 import 时不会执行（和 Java 的 `if (require.main…)` 那种入口守卫类似）
if __name__ == "__main__":
    raise SystemExit(main())
