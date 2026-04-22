# AI-Agent 学习仓

- **学习路线**：[`AI应用开发学习计划-Java与Python双轨.md`](./AI应用开发学习计划-Java与Python双轨.md)  
- **周计划逐日**：[`AI应用开发学习计划-周计划/`](./AI应用开发学习计划-周计划/)  
- **第 0 周 · 第 3 天（收尾）**：见下文 [「第 0 周 · 第 3 天」](#week0-day3) 一节。
- **第 1 周 · 第 6 天（联调）**：Mermaid 时序图、双端各一条入口命令见下文 [「第1周联调与验收」](#week1-acceptance)，以及周计划 [第 01 周第 6 天](AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md#week1-day6)。

## 第1周联调与验收

<a id="week1-acceptance"></a>

> 与周计划 [第 01 周第 6 天](AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md#week1-day6) 对应：**一张时序图**（客户端 → `java-demo` 网关 → 大模型，含同步/流式两条）+ **双端各一条**「入口命令」（Python 为直连脚本的**命令行**，Java 为**带鉴权**的 `curl`）。

| 双端 | 说明 | 一条命令（已配置 DASHSCOPE；Java 需另开终端在 `monorepo-java/java-demo` 下 `mvn spring-boot:run`） |
|------|------|----------------------------------|
| **Python** | 第 1 天同步脚本，**直连**通义/兼容端，不经过 `java-demo` | `cd monorepo-py && conda activate aimodel && python scripts/week01_day1_sync_chat.py "用一句话说你好"` |
| **Java** | 经网关、**SSE 流**（与「同步+流式各一条」中的**流**对齐；同周另有同步 `POST /api/v1/chat`） | `curl -N -s -X POST http://localhost:8080/api/v1/chat/stream -H 'X-API-Key: demo' -H 'Content-Type: application/json' -d '{"prompt":"hi"}'` |

**Function Calling（第 1 周第 7 天，双端）**：Python 跑 `cd monorepo-py && python scripts/fc_min.py`；Java 在 `java-demo` 已起时  
`curl -s -X POST http://localhost:8080/api/v1/fc/chat -H 'X-API-Key: demo' -H 'Content-Type: application/json' -d '{"prompt":"3+5 用工具算"}'`。通义建议 **`LLM_MODEL=qwen-plus`**。详见 [周计划第 7 天](AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md) 与 [java-demo README](monorepo-java/java-demo/README.md)。

更多参数与 DTO 说明见 [monorepo-java/java-demo/README](monorepo-java/java-demo/README.md) 与 [monorepo-py/README](monorepo-py/README.md)。

---

## 目录结构（双栈分仓）

| 目录 | 内容 |
|------|------|
| [`monorepo-py/`](./monorepo-py/) | Python：conda 环境、脚本、后续 RAG/服务等 |
| [`monorepo-java/`](./monorepo-java/) | Java：Spring Boot + Spring AI Alibaba；子工程 [`java-demo`](./monorepo-java/java-demo/) 为第 0 周可运行样例 |

**说明**：**并非** 工具链里的「Git monorepo 工具名」，仅表示**一个仓库里** Java / Python **代码分目录** 管理，避免混放。

---

## 第 0 周 · 第 3 天：双端收尾与验收

<a id="week0-day3"></a>

> 对应周计划 [`第00周-环境与仓库准备.md`](./AI应用开发学习计划-周计划/第00周-环境与仓库准备.md) 中 **「第 3 天（或第 0 周结束日）」**。第 1、2 天已分别跑通 Python、Java 后，本日把**文档、环境变量约定、一键自检** 收齐，便于以后换机器 **15 分钟内** 复现。

### 第 3 天要做的事（ checklist ）

- [ ] **根目录说明**（即本 `README`）：已说明双目录、`monorepo-py` / `monorepo-java` 各自入口、**启动顺序**（见下）。
- [ ] **环境变量模板**：`monorepo-py/.env.example` 已存在；根目录另有 [`env.example`](./env.example) 作为**全仓变量名速查**（**无** 真密钥，可提交）。
- [ ] **密钥仍不入库**：确认本地 `monorepo-py/.env`、系统 `export` 等**未被** `git add`；`.gitignore` 已忽略 `.env`。
- [ ] **双端各验一次**（通义为同一 key 时最省事）：
  1. **Python**（不依赖本机起 HTTP 服务）  
  2. **Java**（需先起 `java-demo`，默认端口 `8080`）

### 推荐启动顺序

| 步骤 | 做什么 | 说明 |
|------|--------|------|
| 1 | 配置密钥 | 终端 `export DASHSCOPE_API_KEY=...` **或** `export AI_DASHSCOPE_API_KEY=...`；Java 的 `application.yml` 会优先 `AI_`，无则回退到 `DASHSCOPE_`。 |
| 2 | 验 Python | `cd monorepo-py` → `conda activate <你的环境>` → `python scripts/health_chat.py` → 应打印回复前 200 字。细节见 [monorepo-py/README](monorepo-py/README.md)。 |
| 3 | 验 Java | 另开终端：`cd monorepo-java/java-demo` → `mvn spring-boot:run` → 浏览器或 `curl` 访问下表 URL。见 [java-demo/README](monorepo-java/java-demo/README.md)。 |

### 一键自检（可选）

若本机已安装 `make` 与 `curl`，可在**仓库根目录**执行（第 0 周第 3 天**可选**任务）：

```bash
# 只测 Python 脚本
make health-py

# 只测 Java（需 java-demo 已启动且 8080 可用）
make health-java

# 先 Python 再 curl Java（java 未启动时后一步会失败，属正常）
make health
```

`Makefile` 同目录已提供，无需配置 `task`。

### 双端成功时的样例

**Python**（标准输出为模型自然语言，最多约 200 字）：

```bash
cd monorepo-py && python scripts/health_chat.py
```

**Java**（JSON，`preview` 为前 200 字）：

```bash
curl -s http://localhost:8080/api/v1/health/llm
```

两路能通即可认为 **第 0 周产出一阶段达成**；若只通一端，在笔记里记清**原因**（key、网络、模型名、端口）再进第 1 周。

### 子文档入口

| 文档 | 用途 |
|------|------|
| [monorepo-py/README.md](monorepo-py/README.md) | Conda、依赖、`health_chat.py` |
| [本页「第1周联调与验收」`#week1-acceptance`](#week1-acceptance) | 第 1 周第 6 天：Mermaid 见 [周计划第6天](AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md#week1-day6)；**Python 一条** + **Java 一条** `curl` |
| [monorepo-java/java-demo/README.md](monorepo-java/java-demo/README.md) | Maven、探活、第 1 周 `POST /api/v1/chat`、**SSE**、**`POST /api/v1/fc/chat`（Function Calling）**、鉴权/限流、DashScope 配置 |
| [env.example](env.example) | 全仓环境变量**名称**速查，复制后勿提交真值 |

---

## 第 0 周快速起（与第 1、2 天关系）

- **第 1 天**：以 Python 为主，见 [monorepo-py/README](monorepo-py/README.md)。  
- **第 2 天**：以 `java-demo` 为主，见 [monorepo-java/java-demo/README](monorepo-java/java-demo/README.md)。  
- **第 3 天**：以本页 [「第 0 周 · 第 3 天」](#week0-day3) 为准，把**文档 + 验收命令** 跑通。  
