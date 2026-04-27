# monorepo-py

本目录为 **Python** 子工程：算法原型、RAG/向量、可选 FastAPI、与 `openai` 兼容调用等，与 `../monorepo-java` **代码分离**。

**代码风格（约定）**：本仓里为你写的 `scripts/` 会尽量带**中文注释**（`#` 单行、`"""` 多行），说明「这句 Python 在干什么」；你本地补代码时若不确定语法，可优先问 IDE / 对注释逐行搜文档。

## 第 0 周：环境

```bash
conda create -n aimodel python=3.10 -y
conda activate aimodel
cd monorepo-py
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 DASHSCOPE_API_KEY 等
python scripts/health_chat.py
```

## 第 1 周：大模型应用地图与 API

- 总览与按日任务：[`AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md`](../AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md)  
- **第 1 天**（同步 + 参数 + 三档超时）：[`week01/README.md`](./week01/README.md) · 入口脚本 [`scripts/week01_day1_sync_chat.py`](./scripts/week01_day1_sync_chat.py)
- **第 2 天**（流式 + 首段延迟 + 自测笔记）：同一 [`week01/README.md`](./week01/README.md) · 入口 [`scripts/week01_day2_stream_chat.py`](./scripts/week01_day2_stream_chat.py)
- **第 6 天**（时序图 + 联调）：Mermaid 与「双端各一条」入口见仓库 [根 `README`「第1周联调与验收」](../README.md#week1-acceptance)；图文在 [第 01 周第 6 天](../AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md#week1-day6)
- **第 7 天**（收尾 + **Function Calling**）：笔记模板 [`week01/day7_本周收尾与FC.md`](./week01/day7_本周收尾与FC.md) · 最小闭环 [`scripts/fc_min.py`](./scripts/fc_min.py)（与 Java `POST /api/v1/fc/chat` 双端对照，见 [java-demo README](../monorepo-java/java-demo/README.md)）

```bash
cd monorepo-py
conda activate aimodel
python scripts/week01_day1_sync_chat.py
python scripts/week01_day1_sync_chat.py "自定义问题"
python scripts/week01_day2_stream_chat.py
python scripts/week01_day2_stream_chat.py 用三句话介绍流式输出
python scripts/fc_min.py
python scripts/fc_min.py "11 加 22 等于多少，用工具算"
# FC 通义建议 LLM_MODEL=qwen-plus（在 .env 或 export），与 Java 端一致
```

## 第 2 周：Prompt 与 LangChain 结构化输出

- 周计划：[`AI应用开发学习计划-周计划/第02周-Prompt与结构化输出.md`](../AI应用开发学习计划-周计划/第02周-Prompt与结构化输出.md)  
- 入口脚本：[`scripts/week02_structured_intent.py`](./scripts/week02_structured_intent.py)（`with_structured_output` + 两版 system，各跑 5 次）  
- 错例与改法模板：[`notes/failures.md`](./notes/failures.md)  
- 依赖：安装 `pip install -r requirements.txt`（含 `langchain-core`、`langchain-openai`）

```bash
cd monorepo-py
pip install -r requirements.txt
python scripts/week02_structured_intent.py
python scripts/week02_structured_intent.py "把会议室从三点改成四点半"
```

## 第 3 周：Embedding、Milvus 与 `/search`

- 周计划：[`AI应用开发学习计划-周计划/第03周-Embedding与向量检索.md`](../AI应用开发学习计划-周计划/第03周-Embedding与向量检索.md)  
- 说明与命令：[`week03/README.md`](./week03/README.md)  
- 语料：`data/corpus.txt`；向量：默认 **Milvus Lite** 单文件 `data/milvus_lite.db`（可改为 `MILVUS_URI` 连独立 Milvus；见 `week03/milvus_settings.py`）  
- `curl` 示例：[`notes/search-samples.md`](./notes/search-samples.md)  

```bash
cd monorepo-py
pip install -r requirements.txt
./week03/ingest.sh
python3 -m uvicorn week03.api:app --host 0.0.0.0 --port 8010
# 另开终端试搜：curl -s -X POST http://127.0.0.1:8010/search -H 'Content-Type: application/json' -d '{"q":"报销","k":3}' | jq .
```

## 结构（随学习可继续补）

- `scripts/` 脚本与第 0 / 1 周实验  
- `week01/`、`week03/` 当周说明与入口  
- `data/`：第 3 周语料与 Milvus Lite 数据文件（`milvus_lite.db` 已 `.gitignore`）  

密钥与**本地**环境变量只放在本目录的 `.env`（已在上级 `.gitignore` 忽略）。
