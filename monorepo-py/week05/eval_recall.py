#!/usr/bin/env python3
"""
第 5 周：在 eval/queries.csv 上算粗 **recall@5**（任一条 rel 进 top-5 即计命中）。

需已 `ingest`、默认走与线上一致的混合检索；在 monorepo-py 下执行：

  PYTHONPATH=. python week05/eval_recall.py
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")


def main() -> int:
    csv_p = _ROOT / "eval" / "queries.csv"
    if not csv_p.is_file():
        print(f"缺少 {csv_p}", file=sys.stderr)
        return 1
    rows: list[dict[str, str]] = []
    with csv_p.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    from week05.hybrid import hybrid_search

    k = 5
    hits = 0
    skip = 0
    for r in rows:
        q = (r.get("q") or "").strip()
        rel = (r.get("rel_chunk_ids") or "").strip()
        if not q:
            continue
        if not rel or rel in ("无", "none", "NONE", "-"):
            skip += 1
            continue
        want = {x.strip() for x in rel.split(";") if x.strip()}
        if not want:
            skip += 1
            continue
        recall_n = int(os.environ.get("RAG_RECALL_FOR_EVAL", "8"))
        pairs = hybrid_search(
            q,
            k_vec=recall_n,
            k_kw=recall_n,
            k_out=k,
        )
        top = [p.id for p in pairs[:k]]
        if want & set(top):
            hits += 1
        else:
            print("miss:", repr(q)[:50], "want", want, "top", top, file=sys.stderr)

    n = len(rows) - skip
    r5 = (hits / n) if n else 0.0
    print(
        f"评估条数(含 rel): {n}  跳过(无 rel): {skip}  命中@5: {hits}  粗 recall@5={r5:.2f}\n"
        "（面试说法示例：我建了小集，粗 recall@5≈0.x，主要失败在短查/同义词/无知识）"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
