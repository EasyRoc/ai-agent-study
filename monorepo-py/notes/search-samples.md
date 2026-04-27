# 第 3 周：`POST /search` 自测样例

> 先 `python -m week03.ingest` 写入 **Milvus**（默认本机 `data/milvus_lite.db`），再 `uvicorn week03.api:app --port 8010`，再执行 `curl`。**本文件为手填/粘贴示例**，以你本机实际 JSON 为准。

## 例 1：报销

```bash
curl -s -X POST http://127.0.0.1:8010/search \
  -H 'Content-Type: application/json' \
  -d '{"q":"报销要多久能到账","k":3}' | jq .
```

## 例 2：会议室

```bash
curl -s -X POST http://127.0.0.1:8010/search \
  -H 'Content-Type: application/json' \
  -d '{"q":"预定会议室 301","k":2}' | jq .
```

## 例 3：经 Java 网关

```bash
# java-demo 已启动且与 APP_VECTOR_BASE_URL 一致
curl -s "http://127.0.0.1:8080/api/v1/vector-demo?q=年假&k=2" | jq .
```

**响应形状**（与第 4 周 RAG 衔接，勿随意改字段名）：

- `results`: `[{ "id", "text", "score" }, ...]`
- `model`: 所用 embedding 模型名
- `memory_layer`: 固定为 `L2_retrieval` 时，表示**本层是 L2 外显/检索记忆**，**不是** L0 对话记忆
