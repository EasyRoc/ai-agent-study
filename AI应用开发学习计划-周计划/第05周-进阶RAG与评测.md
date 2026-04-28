# 第 5 周：进阶 RAG、混合检索与简单评测

> 约 **5～7 个学习日**。目标：**混合检索**（向量 + 关键词/ BM25 至少一种）、**小评测集**、Java 侧 **缓存/幂等/限流** 之一落实。Python 在实现融合与评测脚本时，**能复用 LangChain 的 `EnsembleRetriever`、自定义 `BaseRetriever` 等则优先用**，无则手写融合逻辑亦可，但需在 README **一句话** 说明取舍。

## 本周目标

- Python：在上周语料上增加 **关键词检索** 路径（如 `Whoosh` / `jieba + 倒排` / `rank_bm25` 对已有 chunk 建索引，或 **LangChain 封装的 BM25/混合检索** 若与你版本兼容），与向量结果 **merge+去重+截断**；参数 `alpha` 控制权重可先手写规则（例如前 2 条 BM25 + 前 2 条向量）。
- 准备 **5～20 条** `question, expected_corpus_id 或 关键词` 的 CSV，**人工**标「好/中/差」与一句话原因。
- Java：对 **同一 `question`** 的 RAG 查询做 **5 分钟** 内内存缓存或 Caffeine（key=hash(question)）；`POST` 写类请求若重复提交做 **idempotent key** 占位（可用内存 map）。

## 按日计划

### 第 1 天：关键词索引

- 为每个 chunk 存 `id`, `text`；用 **BM25** 或简单「包含子串」为 fallback（可渐进：先子串，再 BM25）。
- 输出：`keyword_search(q, k)` 列表，结构与向量检索类似。

### 第 2 天：融合策略

- 实现 `hybrid(q, k_vec, k_kw, k_out)`：合并打分（可先 **RRF** 手抄公式或**简单并集截断**）。
- 在相同 3 个 query 上对比：**纯向量 vs 纯关键词 vs 混合**（各写 1 行笔记）。

### 第 3 天：小评测集

- 建 `eval/queries.csv`：列如 `q, rel_chunk_ids(分号), notes`。
- 写脚本 `eval.py`：对每条 `q` 调混合检索，看 `rel` 是否出现在 top5；输出 **recall@5** 粗略数。
- 不求高分，**求有数字可讲**（面试说法：「我建了 15 条小集，粗 recall@5=0.6，后面主要失败在 xx」）。

### 第 4 天：长任务与队列（示意）

- 若 RAG+长文生成慢：在 Python 或 Java 中实现「**202 Accepted** + `taskId` + 轮询 `GET /task/{id}`」（不必真用 Kafka，**接口形态**到即可），或
- 写设计文档 1 页：若上 Kafka，**topic 名、message 体** 长什么样（为第 7 周铺垫）。

### 第 5 天：Java 缓存

- 引入 Caffeine：`maximumSize`, `expireAfterWrite` 合理值。
- 加一层 `X-No-Cache: 1` 时跳过缓存（调试用）。

### 第 6 天：Java 幂等（选业务）

- 场景：用户「同一次提交生成报告」`clientRequestId` 重复时只返回**同一** `resultId`。
- 实现：内存 `ConcurrentHashMap` + TTL（**演示级**即可）。

### 第 7 天：周总结

- 一页 `improvements.md`：**检索失败** 的 3 类原因（分块太粗/未覆盖/同义词等）与下步计划（第 6 周可引入 Agent 扩写问法——预告）。

### 记忆架构（**建议**本日写草稿）

- 起草 `docs/memory-architecture.md`：**5 行内** 写清 **L0**（`session`、保留几轮）、**L2**（chunk 的 `tenant/scope` 元数据）、**L3**（未做则写原因）。详见 `[记忆架构-索引](./记忆架构-索引.md)`。
- **L1 摘要**（**选做**）：补「多轮超阈值则**压摘要**」的伪代码或**真**实现，与第 2 周衔接。

## 周产出物

- `eval/queries.csv` + 一次 `eval.py` 运行输出（可贴到 md）。
- Java 缓存 +（可选）幂等 demo。
- `docs/memory-architecture.md` **草稿**（**可与**下栏合并为一条**验收**）：分层图 **ASCII/Mermaid 均可**。

## 完成标准

- 能讲清：**为何**要混合检索、你选的融合策略是 **可解释** 的（不依赖「黑盒 rerank 就行」一句带过）。

## 与第 6 周衔接

当检索仍不准时，第 6 周可用 **Agent** 先「改写问句」或「多步检索」。

## 选做

- 元数据：给 chunk 加 `tag: HR|Finance`，检索时加 filter（**简单字符串过滤**即可）。

