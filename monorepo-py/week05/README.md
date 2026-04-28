# 第 5 周：进阶 RAG、混合检索与简单评测

与 [`../../AI应用开发学习计划-周计划/第05周-进阶RAG与评测.md`](../../AI应用开发学习计划-周计划/第05周-进阶RAG与评测.md) 对齐。

## 合并策略（为何不用 LangChain EnsembleRetriever）

本仓用 **BM25（`rank-bm25` + `jieba` 分词）** 在**与 Milvus 相同 chunk id** 上建索引，与向量路结果做 **RRF 融合**；公式在 `week05/hybrid.py` 中显式，便于说清「**不是**只信一个黑盒分数」。需要框架封装时可自行换成 `EnsembleRetriever`，需自行对齐 `chunk-0` 与元数据。

## 环境变量

| 变量 | 含义 |
|------|------|
| `RAG_HYBRID_ENABLED` | 默认 `true`；`false` 时检索退化为**纯 Milvus 向量** |
| `RAG_HYBRID_KW` | 关键词路取前多少条进 RRF；`0` 或空表示 `max(4, min(topK, 32))` |
| `RAG_RRF_K` | RRF 常数，默认 `60` |

## 评测

```bash
cd monorepo-py
PYTHONPATH=. python week05/eval_recall.py
```

语料在 `eval/queries.csv`；需与 `data/corpus.txt` 一致且已 `python -m week03.ingest`。

## 长任务 API

- `POST /rag/tasks` body 同 `/rag/ask` 的 question/topK/sessionId，返回 202 与 `taskId`。  
- `GET /rag/tasks/{taskId}` 轮询结果。  
- Kafka/队列形态见 [`../../docs/week05-long-task-kafka.md`](../../docs/week05-long-task-kafka.md)。

## Java

网关侧 **5 分钟 Caffeine 缓存**、`X-No-Cache` 旁路、`clientRequestId` 幂等见 `monorepo-java/java-demo` 的 `RagServiceClient` 与 README。
