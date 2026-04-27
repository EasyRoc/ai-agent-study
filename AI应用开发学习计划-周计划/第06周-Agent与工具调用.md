# 第 6 周：ReAct、Function Calling、MCP、Skills 与工具调用

> 约 **5～7 个学习日**。本周为**流行技术**集中周：先 **Function Calling** 工程闭环，再 **ReAct 轨迹**，再 **MCP 暴露工具**，再 **Skill 声明** 把能力「产品化」。总索引见 [`流行技术索引`](./流行技术索引-ReAct-FunctionCalling-MCP-Skills.md)；**记忆** 与 **L0/L3** 见 [`记忆架构-索引`](./记忆架构-索引.md)。

## 本周总目标

- **Function Calling（必做）**：**Python、Java 各 1 条**可运行链路，**均用** 原生 `tools` / `@Tool` 等，**不**以「仅 prompt 里自写 ReAct 文本」作为唯一落地方案（可做**对照实验**，不能替代 FC）。
- **ReAct（必做）**：在 Python 用 **ReAct 风格 Agent**（如 LangChain `create_react_agent` 或当前文档推荐 API）跑通；**保存** 含 **thought / action / observation** 或 `tool_calls` 轨迹的日志。
- **MCP（必做，最小）**：实现**一个** MCP Server（`stdio` 或官方模板），**至少 1 个 tool**（如代理已有 `/search`）；用 **MCP Inspector** 或**最小 client** 成功 `tools/call` 一次（录屏或日志路径写入 `README` 片段）。
- **Skills（必做，文档级）**：仓库内 `skills/<name>/SKILL.md`：写清 **触发/意图**、**分步 SOP**、**依赖工具名**；理解 **Skill ≠ 单个 tool**，是**编排+契约**。
- **业务题**：与前几周同场景——「**请假**相关检索 + **天气/计算器** mock 外部 API」类**多意图**问题 1 道，对比 **无工具 RAG** 与 **Agent+工具**。
- **与记忆**：**ReAct 多轮** 必须**吃** 第 2 周 **L0**（或明确「无状态每轮全量」+ **tradeoff** 一句）；**L3 选做**：`save_user_preference` 等 **Tool 写入** 与读回（**mock DB** 即可）。

## 概念表（本周末要能用面试话讲）

| 概念 | 你要能说完的一句 |
|------|------------------|
| **Function Calling** | 模型在**单轮**响应里**结构化**指定工具与参数，**我执行**后**回注** `tool` 消息再续写。 |
| **ReAct** | **多轮**的「想→做→看观察」循环，**通常每步**用 **FC** 做 Action，**不是**和 FC 二选一。 |
| **MCP** | **标准**发现/调用/资源协议；我的业务 HTTP 是 **MCP tool 的 handler**；**不替代** RAG/业务。 |
| **Skills** | **何时、用哪几个子能力、怎么串** 的**声明**（人读+可版本化），工具在下面 **MCP/HTTP** 层实现。 |

## 按日计划

### 第 1 天：Function Calling 双端（无框架 Agent）

- [ ] **Python**：**路线 A** —— 用 **LangChain** 的 `bind_tools` + **Tool** 定义，跑通**两工具**（如 `get_leave_policy` 内调第 3～4 周 `search`、`get_weather` mock）；**路线 B**（**对照**）：手写 `openai/兼容` 的 `tool_calls` 执行器。**至少一条** 路线在仓库可运行并打日志。  
- [ ] **Java**：用 **Spring AI Alibaba**（`spring-ai-alibaba-starter-dashscope` + 已引入的 **`spring-ai-alibaba-agent-framework`**）在 **Function Calling** 与官方**工具/Bean** 注册方式下，注册 2 个 **Tool**（如 `@Tool` 或**当前版本** 推荐写法），对外 `POST /api/v1/agent/fc`（名可自拟），在服务端执行工具、再调 `ChatClient`**直到** 出终答或达 max 轮；**不** 另开 LangChain4j 实现对比版（除非有精力做**附注**）。
- [ ] 产出：「**FC 和手写 JSON 的 ReAct 假动作** 有什么**工程差异**」3 bullet 写 `notes/fc-notes.md`。

### 第 2 天：ReAct 与轨迹

- [ ] **Python**：用 **LangChain** 等**现成** ReAct Agent 跑**同一**多意图题；**打开** `verbose` 或**回调**里记录每一步。
- [ ] 保存 `notes/react-trace.log` 片段（脱敏）：至少 **2 次** 工具调用**完整**可辨。
- [ ] 对比表 **1 行/格**：`纯单轮 RAG` | `多轮仅 FC` | `ReAct+FC` 各适用场景。

### 第 3 天：MCP Server 最小

- [ ] 读 **MCP** 规范中的 **Tools** 章节（**官方仓库** 或你选用语言的 SDK 文档，30min～1h）。
- [ ] 用 **MCP Python SDK** / **TypeScript 模板** 等，起一个 **MCP Server**，注册 **tool**：`knowledge_search(q)` 内部 `HTTP` 调你第 3 周 `search`（或**临时**返回固定 JSON）。
- [ ] 用 **Inspector** 或 `mcp` 客户端 调通 `tools/list` 与 `tools/call`；截图或**文本日志**进 `docs/mcp.md`。

### 第 4 天：MCP 与 ReAct/FC 的衔接（概念 + 最小编排）

- [ ] 在 `docs/mcp.md` 补一段：**若** Agent 在「应用侧」，**MCP 放** 工具提供侧，**你的 Java 网关**是否还要再包一层？（**写清边界**，无标准答案，但要**自洽**）。
- [ ] **选做**：让 Python ReAct 的**一个** tool 实现为「**调用本机 MCP 暴露的** tool」（可用子进程/HTTP 桥，**不**求优雅，**能**说明集成思路即可）。

### 第 5 天：Skills 声明

- [ ] 新建 `skills/leave_and_weather/SKILL.md`（目录名可自拟），包含：**名称**、**description（何时用）**、**步骤 1-2-3**、**需工具**：`knowledge_search`, `get_weather` 等，与上面 FC 工具**同名**可利于后续**自动化**（不必真自动）。
- [ ] 写 100 字：**Skill 与**「裸 tools 列表给模型」的**产品差异**（给用户/给团队的**可维护性**）。

### 第 6 天：联调、异常、边界

- [ ] 工具 **5xx / 超时**：tool 的 handler 返回**结构化** `error` 给模型**再续写**（不崩进程）。
- [ ] **最大步数** N（如 5）打满时：用户可见**截断**说明 + 日志 `max_steps`。
- [ ] **选做：Guardrails**：明显敏感 query **不走** 工具，直接 `content_filter` 消息（**硬规则**即可）。

### 第 7 天：周产出与 README

- [ ] `README` 增加「第 6 周」：**如何**起 Python FC / Java Tool / **MCP Server**（`stdio` 命令行**复制可用**）。
- [ ] 更新 `notes/agent-vs-rag.md`：同一复合问题，**RAG 一次** vs **ReAct+工具** 摘要对比（上周若已有可**合并**）。

## 周产出物（强验收）

- [ ] `notes/fc-notes.md` + `notes/react-trace.log` 片段 + `docs/mcp.md`（含**至少一次** `tools/call` 成功证据）。
- [ ] `skills/.../SKILL.md` 1 份。
- [ ] 对比表文件：`docs/compare-rag-fc-react-mcp-skill.md`（Markdown 表即可，**四列**：无工具RAG、FC 多步、ReAct+FC、经 MCP 暴露时各 **1-2 句**）。

## 完成标准

- 面试 **2 分钟** 内能说：**FC / ReAct / MCP / Skills** 各解决什么**层**的问题；并指着自己仓库说「**哪几个文件** 对应哪块」。

## 与第 7 周衔接

多步+慢工具 自然导向 **长任务/队列**；在 `docs` 里可标注「第 7 周将把 **Agent 中某步** 改为**异步 job**」。

## 与第 9 周衔接

综合项目**可选**把 RAG/检索 **以 MCP tool** 暴露，或**保留** HTTP，**在 README 二选一**写死即可。

## 选做

- 把 **MCP** 的 `resources` 读一份静态 `policy.md` 进上下文（**体会** 与 RAG 的**边界**；不必做细）。
