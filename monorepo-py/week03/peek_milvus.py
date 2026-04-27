#!/usr/bin/env python3
"""
在终端里快速「瞄一眼」Milvus 里 week03_hr 的数据（与 ingest 使用同一 connection_args）。

用法（在 monorepo-py 根目录）：

  python -m week03.peek_milvus

不会起 Web 服务；需已 ingest 过。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    p = _ROOT / ".env"
    if p.is_file():
        load_dotenv(p)
    else:
        load_dotenv()

    from pymilvus import MilvusClient

    from week03.milvus_settings import COLLECTION_NAME, connection_args

    args = connection_args()
    client = MilvusClient(**args)

    if not client.has_collection(COLLECTION_NAME):
        print(f"集合不存在: {COLLECTION_NAME}，请先 python -m week03.ingest", file=sys.stderr)
        return 1

    info = client.describe_collection(COLLECTION_NAME)
    print("=== describe_collection（字段与部分元信息）===")
    print(json.dumps(info, indent=2, ensure_ascii=False, default=str))

    try:
        stats = client.get_collection_stats(COLLECTION_NAME)
        print("\n=== get_collection_stats ===")
        print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print("\n=== get_collection_stats（跳过）===", e)

    # LangChain 写入时 ids 为 chunk-0, chunk-1, …
    n = 32
    ids = [f"chunk-{i}" for i in range(n)]
    rows = client.get(COLLECTION_NAME, ids=ids, output_fields=None)
    print(f"\n=== get(前 {n} 个 chunk-i 主键，可能少于入库条数) ===")
    for row in rows:
        rid = row.get("id") or row.get("pk")
        # 有正文则打印截断
        t = row.get("text", "")
        if t:
            t = t[:200] + ("…" if len(t) > 200 else "")
        vec = row.get("vector")
        if vec is not None and hasattr(vec, "__len__"):
            head = list(vec[:3]) if len(vec) >= 3 else list(vec)
            vec_s = f"dim={len(vec)} 前3维={head}"
        else:
            vec_s = "无"
        print(f"- {rid!r}  text={t!r}  vector: {vec_s}")
    if not rows:
        print("（get 无结果，可再跑 ingest 或检查 collection 主键名是否为 pk）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
