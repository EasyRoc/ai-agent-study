# 第 4 周：RAG（检索 + 生成 + 引用）

与 [`../../AI应用开发学习计划-周计划/第04周-RAG完整链路与引用.md`](../../AI应用开发学习计划-周计划/第04周-RAG完整链路与引用.md) 对齐。

## 做什么

- **`POST /rag/ask`**（挂在 **`week03.api:app` 同一进程**，默认与 `/search` 同端口 **8010**）  
  - Body: `question`、可选 `topK`（默认 4）、可选 `sessionId`：传时启用 **L0 短期记忆**（本进程内最近若干轮问答摘要，注入 prompt 便于多轮指代；**不**写入 Milvus，见 `week04/session_memory.py`）  
  - 响应 `citations` 为**送入 LLM 的全量检索条**（与 `topK` 条数一致）；`cited_ids` 为模型在 structured 里**声明引用**的 id 子集，条数可更少  
  - 内部：Milvus 初检（条数可大于 `topK`）→ 可选 **DashScope `qwen3-vl-rerank`** 重排为 `topK` 条 → 拼 system/user → **通义** `with_structured_output`（Pydantic `citation_ids`）→ 组装 `citations: [{id, excerpt}]`  
- 记忆分层：响应 `memory_layer: L2_rag` 表示**制度事实**仍来自检索知识库（L2）；若带 `sessionId`，另在 prompt 中注入 **L0 短期对话**（进程内、不入 Milvus，与 L2 正交）。

## 如何起服务

与 week03 相同，一条命令即可带齐 `/search` 与 `/rag/ask`：

```bash
cd monorepo-py
python -m uvicorn week03.api:app --host 0.0.0.0 --port 8010
```

自测与跨端验收见 [仓库 `docs/rag-samples.md`](../../docs/rag-samples.md)。

## 环境变量（可选）

| 变量 | 含义 |
|------|------|
| `RAG_TEMPERATURE` | 生成温度，默认 `0.3` |
| `RAG_LLM_TIMEOUT_SEC` | LLM 调用超时（秒），默认 `90` |
| `RAG_RERANK_ENABLED` | 是否对初检结果做重排，默认 `true` |
| `RAG_RERANK_MODEL` | 重排模型，默认 `qwen3-vl-rerank`（需与百炼文档一致） |
| `RAG_RERANK_INSTRUCT` | 可选，控制排序任务说明，见百炼 **文本排序** API 文档 |
| `RAG_RECALL_TOP_K` | 向量初检条数；不设时约为 `max(8, 2*topK)` 且与 `topK` 比较后 **≤ 100**（`qwen3-vl-rerank` 单请求 document 上限） |
| `RAG_SESSION_MEMORY_ENABLED` | 是否启用 L0 短期记忆，默认 `true`（无 `sessionId` 时仍无记忆） |
| `RAG_SESSION_MAX_TURNS` | 每会话保留最近几轮「问+答」，默认 `5` |
| `RAG_SESSION_USER_MAX_CHARS` / `RAG_SESSION_ANSWER_PREVIEW_CHARS` | 注入 prompt 时截断用户问/助手答，默认 `500` |

## Rerank

使用 **`dashscope.TextReRank`** 与 `qwen3-vl-rerank`；关闭或失败时回退为向量初检结果的前 `topK` 条。依赖见根目录 `requirements.txt`。
