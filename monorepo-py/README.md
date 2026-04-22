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

## 结构（随学习可继续补）

- `scripts/` 脚本与第 0 / 1 周实验  
- `week01/` 当周说明与索引  
- 后续可增：`app/`（FastAPI）、`data/`（样例，勿提交大文件）等  

密钥与**本地**环境变量只放在本目录的 `.env`（已在上级 `.gitignore` 忽略）。
