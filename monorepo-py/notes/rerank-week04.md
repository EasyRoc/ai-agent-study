# 第 4 周：Rerank（DashScope + qwen3-vl-rerank）

在 `run_rag` 中，向量先按 `RAG_RECALL_TOP_K`（未设时约为 `max(8, 2*top_k)`，上限 100）初检，再调用 **`dashscope.TextReRank`，模型默认可配 `RAG_RERANK_MODEL=qwen3-vl-rerank`**，截断为请求里的 `top_k` 后送 LLM。

- 需 **`DASHSCOPE_API_KEY`** 与 `pip install` 的 **`dashscope`**。
- 关 rerank：设 `RAG_RERANK_ENABLED=false` 则仅用向量序截断为 `top_k`。
- 失败（网络/额度/SDK）：**回退为向量序**，不阻断整条 RAG（见 `week04/rerank_qwen.py` 日志）。

**第 5 周** 若上 BM25+向量混合、缓存与长任务，可继续在 recall 后换其它 rerank 或自训排序器。
