# 第 3 周：Embedding 与向量检索

> 约 **5～7 个学习日**。目标：**分块 + 嵌入 + 向量库「入库与相似检索」**；Java 以 **HTTP 调 Python 向量服务** 为推荐路径（你也可在 Java 用 **Spring AI / Spring AI Alibaba** 已提供的**向量/检索** starter，**二选一做深**即可，**以当前 Alibaba 文档是否暴露该能力** 为准）。

## 本周目标

- Python：10～20 条可复现的短文本（或 2～3 个长文分块后）写入 **Chroma** 或 **FAISS**；提供 `/embed`（可选）与 `/search`（必须）。在说明中**标明** 本层为 **L2 外显/检索记忆**（**组织/文档知识**），**不是** 第 2 周 **L0 会话** 的替代（见 [`记忆架构-索引`](./记忆架构-索引.md)）。
- Java：`RestTemplate`/`WebClient` 调 `POST /search`；入参 `query`, `topK`；出参 `chunks` 列表含 `id`, `text`, `score`。
- 记录：**向量维度、所用 embedding 模型名** 写在 `README`。

## 分块策略（至少实现一种）

- 固定 `chunk_size=300` 字 / `overlap=50`；或
- 按换行/段落分块。  
本周**不必**上 LangChain 的复杂 splitter，**能复现**即可。

## 按日计划

### 第 1 天：Embedding 调用通

- [ ] 选定 embedding：`text-embedding-3` 系 / 通义 / 智谱 等，以你已有 key 为准。
- [ ] Python：函数 `embed(text: str) -> list[float]`，**打印维数**并写入常量。

### 第 2 天：向量库建库

- [ ] 安装 Chroma（持久化到 `./data/chroma`）或 FAISS + 自建 id 映射 json。
- [ ] 准备数据：`data/corpus.txt` 或 10 行 JSON，**每行一条**可检索语料（如「请假流程」「报销流程」…）。
- [ ] 脚本 `ingest.py`：读入、分块、批量化 embed、写库、打印插入条数。

### 第 3 天：检索 API

- [ ] `POST /search`：body `{ "q": "...", "k": 3 }` → 返回 `results: [{id, text, score}]`。
- [ ] 用 `uvicorn`+`FastAPI` 或轻量 `flask` 即可。
- [ ] 用 `curl` 自测 3 个 query，保存响应片段到 `notes/search-samples.md`。

### 第 4 天：Java 调用层

- [ ] 配置 `vector.baseUrl=http://localhost:8xxx`。
- [ ] `VectorClient` 封装 `search(q, k)`，DTO 与 Python 对齐。
- [ ] 新建 `GET /api/v1/vector-demo?q=报销` 返回反序列化结果（可不做鉴权，内部 demo）。

### 第 5 天：错误与空结果

- [ ] 空库 / 无结果时：Python 返回 `[]`，Java 返回 200 + 空列表，**不 500**。
- [ ] 超时：Java `WebClient` 设置 5s 超时，超时返回 **502 或** 业务码 `VECTOR_TIMEOUT`（你定规范）。

### 第 6 天：可复现与数据重置

- [ ] `ingest.sh` 或文档：删除 `data/chroma` 后如何**一键重建**。
- [ ] 把「10 条可检索」在 README 列出**前 2 个 query 示例**。

### 第 7 天：与下周衔接预习（不做实现）

- [ ] 读 1 篇 RAG 简介：知道 **检索到的 chunk 要拼进 prompt** 即完成预习。

## 周产出物

- [ ] `ingest` + `search` 可复现；Java 能展示检索 JSON。
- [ ] `README`：embedding 模型、维度、端口。

## 完成标准

- 新 clone 一人在 **15 分钟** 内能完成 ingest + search + Java 调通（可依赖你写好的 `README`）。

## 与第 4 周衔接

第 4 周在检索后接 **LLM 生成**；本周 `search` 返回结构尽量**稳定**（字段名不要改来改去）。

## 选做

- 记录每次 embed 的 **batch 数** 与总耗时，为第 8 周成本埋点做准备。
