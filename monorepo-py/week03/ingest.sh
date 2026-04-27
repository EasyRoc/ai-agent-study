#!/usr/bin/env bash
# 第 3 周：一键重新入库 Milvus（drop_old 在 ingest 内会替换同名 collection；可选先删本地 Lite 库文件彻底清空）
set -euo pipefail
cd "$(dirname "$0")/.."
# 可选：彻底清空本地 Milvus Lite
# rm -f data/milvus_lite.db data/milvus_lite.db-journal
echo "开始写入 Milvus（连接见 .env 与 week03/milvus_settings.py）…"
python3 -m week03.ingest
echo "完成。请启动: python3 -m uvicorn week03.api:app --host 0.0.0.0 --port 8010"
