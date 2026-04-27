# AI 应用开发系统学习计划（Java + Python 双轨）

> 面向：有 Java 后端与模型集成经验，希望系统补齐「RAG / Agent / 工程化」并同时巩固 Java 与 Python 的 AI 应用开发能力。  
> 周期：建议 **8～12 周**；若时间紧可只执行加粗周次。  
> 原则：**同一套业务 Demo，Python 做快速验证与生态覆盖，Java 做生产形态接口与现有技术栈对齐。**

**逐周细化文档（按日任务、周产出、衔接说明）**：[`AI应用开发学习计划-周计划/README.md`](./AI应用开发学习计划-周计划/README.md)（含第 0～10 周共 11 份周历 + [`记忆架构-索引.md`](./AI应用开发学习计划-周计划/记忆架构-索引.md) 等速查页）。

---

## 一、双轨学习如何分工

| 维度 | Python 侧重 | Java 侧重 |
|------|-------------|-----------|
| 定位 | 原型、脚本、RAG/Agent 生态（**LangChain 为主、LangGraph 按需**）最先跑通 | 与现有微服务、Spring 生态、企业内对接方式一致 |
| 建议栈 | **`langchain` + `langgraph`（编排/多步/异步** 场景）**+** 向量（Chroma/FAISS 等，见周计划）；`openai` 兼容仅作**旁路/对照** | **`Spring Boot 3.5` + [Spring AI Alibaba](https://github.com/alibaba/spring-ai-alibaba)**：`spring-ai-alibaba-bom` + **`spring-ai-alibaba-extensions-bom`**（**DashScope** 等）**+** `spring-ai-bom`；**至少** `spring-ai-alibaba-starter-dashscope` + `spring-ai-alibaba-agent-framework`；**结构化输出** 以 **Spring AI Structured Output** 实现（**第 2 周**起贯穿）；**不** 与 **LangChain4j** 混用深挖） |
| 每周节奏 | 约 **50% 时间** 写 Python 小实验 | 约 **50% 时间** 在 Java 中复现同一能力或做网关/适配层 |

同一周 **共用同一小目标**（例如「本周完成最小 RAG」），先 Python 通，再 Java 接 HTTP/RPC，避免学两套无关教程。

### 流行技术对照：ReAct、Function Calling、MCP、Skills

> 与逐周表中的「**Agent/工具/协议**」列对应；更细的**面试对照**见 [`AI应用开发学习计划-周计划/流行技术索引-ReAct-FunctionCalling-MCP-Skills.md`](./AI应用开发学习计划-周计划/流行技术索引-ReAct-FunctionCalling-MCP-Skills.md)。

| 技术 | 是什么（极简） | 本计划**主要**落在第几周 | 和彼此关系 |
|------|----------------|-------------------------|------------|
| **Function Calling**（**Tool / Tools**） | 模型返回**结构化**的「调哪个工具、传什么参」；**你的代码**执行后，把**结果回注**再让模型说人话。 | **1** 概念+最小；**6** 双栈**必做** | 是多数 Agent **落地** 的**底层**调用形态（OpenAI/兼容 API 的 `tool_calls` 等）。 |
| **ReAct** | **Reasoning + Acting**：**思考 → 行动（工具）→ 观察** 多轮，直到可回答；可用 **多轮 Function Calling** 实现。 | **6**（Python 里显式跑 **ReAct 轨迹**） | **范式/循环**；**不是**和 FC 二选一，而是常**用 FC 实现** 每一跳 Action。 |
| **MCP**（Model Context Protocol） | 用**标准协议**把**工具/资源/提示** 做成 **MCP Server**，**客户端**（IDE、自研 Agent）**发现**与**调用**；减少「一项目一坨 REST」的**重复**对接。 | **6** 读规范+**1 个**最小 Server；**9** 综合项目**可选**接入 | 工具可以仍是 **RAG/HTTP** 的**封装**；MCP 管**暴露与发现**，不管业务逻辑本身。 |
| **Skills**（**技能包**） | 把「**何时用、分几步、用哪些工具**」**声明** 成**可发现** 的模块（如 `SKILL.md` + 元数据），偏**产品/编排** 层。 | **6** 写 1 份最小 **Skill 声明**；**9** 可映射为「**技能路由**」**选做** | **高一层**：下面是 **Tools/FC**；**侧面** 可与 **MCP tools/list** 对齐，但**不**强绑定。 |

**学习顺序建议**：先 **Function Calling** 跑通 → 再 **ReAct 循环** 里「看清每一步」 → 用 **MCP** 把工具**用协议暴露**（体会与裸 REST 的差异） → 用 **Skills** 把「**场景级**」**打包** 给**人或** Agent 用。

### 记忆架构（Memory Architecture）在计划中的位置

> 详细分层、与 RAG 的区分、反模式见 [`AI应用开发学习计划-周计划/记忆架构-索引.md`](./AI应用开发学习计划-周计划/记忆架构-索引.md)。

| 层次 | 含义（极简） | 本计划**主要**练在第几周 |
|------|--------------|-------------------------|
| **L0 工作/短期记忆** | 多轮 `messages`、**滑窗/截断**、按 `sessionId` 存取 | **2**（必）、**6**（与 Agent 多轮） |
| **L1 摘要记忆** | 对话过长 → **压成 summary** 再进上下文 | **2** 选做、**5** 可深化 |
| **L2 外显/检索记忆** | **RAG/向量库** = 文档与组织知识，**非**用户脑内日记 | **3～5** |
| **L3 长期/用户事实** | 用户偏好、可被**显式写入** 的事实（表/向量+`userId`） | **5** 概念+轻量、**6** **Tool 写入** 选做 |
| **L4 隔离与治理** | `tenantId`/`userId`、**TTL、可删除**、与审计/合规 | **5～6** 设计、**8** 必能讲 |

**建议**：第 **5 周** 末起草 `docs/memory-architecture.md`，**第 9 周** 综合项目里**用 1 张图+1 段话** 写清你 Demo 的 **L0～L2** 至少，**L3 选做**。

---

## 二、前置准备（第 0 周，2～3 天）

| 任务 | Python | Java |
|------|--------|------|
| 环境 | Python 3.10+、**`conda`（推荐）** 或 `venv`/`uv`、`pip` | JDK 17+、Maven 或 Gradle、IDEA |
| 账号/密钥 | 任一大模型云 API 或 OpenAI 兼容端点，**注意配额** | 同上，配置放环境变量，不入库 |
| 仓库 | 在仓库中建立 **`monorepo-py/`** 与 **`monorepo-java/`**，**代码分目录**；子工程名可自定（如 `monorepo-java/java-demo`） | 同上 |

**本周产出**：两个 Hello World：Python 调一次聊天 API；Java 用 **Spring AI Alibaba**（`ChatClient` 等，以官方样例为准）调同一次（流式 optional）。

---

## 三、周计划总表（10 周）

| 周次 | 主题 | Python 学练重点 | Java 学练重点 | 周产出物 |
|------|------|-----------------|---------------|----------|
| **1** | 大模型应用地图与 API 设计 | 官方 SDK 对话、**流式**、超时与重试；**选做**一次原生 **`tools`/`tool_choice`** 最小调用，理解**Function Calling** 与多轮续写 | Controller 层：鉴权占位、**SSE** 或流式响应封装 | 笔记：补全/对话/**Function Calling 落点** + 1 张请求时序草图 |
| **2** | Prompt 与结构化输出 | **LangChain** `with_structured_output` / Pydantic；**L0 短期记忆**：`sessionId`、**滑窗/截断**；手写 JSON 解析仅作**对照** | **Spring AI Structured Output** + 模板外置 + **`spring-ai-alibaba-agent-framework`** 就位；`ChatClient` **强类型** 结果 + **L0** 滑窗进上下文 | 类型化产出 + `memory-l0-l1` 说明；**不** 以「仅字符串重试」为主验收 |
| **3** | Embedding 与向量库入门 | **LangChain**：`Embeddings` + `TextSplitter` + `VectorStore`；**L2** 与 L0 **分桶** | HTTP 调 Python **或** Spring AI Alibaba 向量能力（**二选一**深）| 入库+检索 + **1 段话**：L2 与 L0 区别 |
| **4** | RAG 完整链路 | **LangChain** 检索链 / **LangGraph** 节点化；**structured output** 产引用；RAG=**L2 读路径** 在图里**写清** | `ChatClient` +（聚合 **或** 本地）生成；**Structured Output** 定义 **citations DTO**；`sessionId` 与 `knowledge` **分维** | 可演示 RAG+**图示中标注 L2** |
| **5** | 进阶 RAG 与**记忆** | 混合检索（**优先**用 LangChain retriever/ensemble **若**版本匹配）+ 评测；**L1/L3** 同前表 | 缓存/幂等；与 Spring AI Alibaba 栈**一致** | 评测表 + `memory-architecture.md` **草稿** |
| **6** | **ReAct、Function Calling、MCP、Skills** 与**记忆写入** | **LangChain** `bind_tools` + ReAct/Agent；**L3 选**；**L0 依赖** | **Spring AI FC** + **agent-framework**；Tool 经 Java **鉴权**（演示） | FC/ReAct/MCP/Skills 笔记 + 可选记忆写入时序图 |
| **7** | 异步、削峰、长任务 | 长任务可包含「**构建索引/摘要记忆**」等慢步骤（概念） | Kafka + 状态机 | 状态图 + **可标注** 哪些任务会**改** 记忆/索引 |
| **8** | 可观测、成本、**记忆合规** | Token/latency、Guardrails + **记忆数据 PII、留存、删除**、**按用户导出/删** 设计口径 | MDC/切面；**不落库** 的敏感**对话** 策略（**截断/脱敏**） | 日志字段说明 + **记忆留存** 1 段政策说明（Demo 级） |
| **9** | 综合项目 | **README** 中 **1 张记忆架构图**（L0～L2 必、L3 选）+ 与 RAG/Agent 关系 **1 段** | 网关侧 **session** 与 鉴权 一致 | 录屏+README **必含** 记忆段 |
| **10** | 简历与面试 | 准备「为什么双栈」：*Python 做验证与数据侧、Java 做在线服务* | 同左 + STAR 写项目、模拟面试 20 道场景题 | 更新简历 + 面试题纲 |

**压缩为 6 周时**：重点执行第 **1、2、3、4、6、9** 周；第 5、7、8 可合并为「RAG 进阶 + 可观测大杂烩一周」。

---

## 四、按周细化任务（可打勾使用）

### 第 1 周：地图 + 流式

- [ ] **Python**：OpenAI 兼容或厂商 SDK 完成同步与流式两种调用；打印首 token 延迟。
- [ ] **选做：Function Calling 最小闭环**：`chat` 请求带 `tools=[{name, description, parameters}]`，模型返回 `tool_calls` 后，你在本地**执行** mock 函数，再拼 `role=tool` 消息**二次**请求，得到最终自然语言；理解**与纯多轮对话**的差异（**第 6 周**会双端必做）。
- [ ] **Java**：暴露 `POST /chat` 与 `GET /chat/stream`（或 SSE），下游转发至模型；FC 在 Java 侧**第 6 周**再强制，本周**不强制**。
- [ ] **产出**：时序图（用户 → 网关 → 模型 → 落库/不落库）；若做 FC，**另画**「模型 → **工具执行器** → 再回模型」小图。

### 第 2 周：Prompt 与结构化输出

- [ ] **Python**：同一业务问题用 2 版 Prompt 对比；**优先** **LangChain** 的 **structured output**（Pydantic / `with_structured_output`）；**对照** 可选保留「手撕 JSON + 重试」一条脚本。
- [ ] **Java**：Prompt 外置 + **Spring AI Structured Output** 绑定 DTO/Bean + **`spring-ai-alibaba-starter-dashscope`** 与 **`spring-ai-alibaba-agent-framework`**；字符串解析 + 重试**仅**作兜底。
- [ ] **L0 短期记忆（必做，轻量）**：为聊天接口增加 `sessionId`（或 `conversationId`）；**只** 将「最近 N 轮」或**截断**后消息列表拼进请求；在代码或 `README` 写清 **N 或 字符 ceiling** 规则。
- [ ] **L1 摘要（选做）**：当轮数 **大于** 某阈值，把更早轮次**换** 成 1 段 `summary`（可调用模型生成），再与最近轮**合并** 进上下文。
- [ ] **产出**：错误样例 3 个与改法；**另**：`docs/memory-l0-l1.md` 或同目录笔记中 **3 行** 说明「无记忆 / 有滑窗 / 有摘要」差异。

### 第 3 周：Embedding 与检索

- [ ] **Python**：**优先** **LangChain** 的 `Embeddings` + `VectorStore` + 分块器；`sentence-transformers` 等仅作替换选项；**在文档或代码注释** 标明：本层为 **L2 外显/检索记忆**，**不** 替代第 2 周 **L0**。
- [ ] **Java**：通过 RestTemplate / WebClient 调 Python 的 `/embed` 与 `/search`，或 **Spring AI / Spring AI Alibaba 提供的向量/检索**能力 选一种，避免三套向量实现。
- [ ] **产出**：10 条短文本可检索、可复现；**1 段话**（可贴 README）：**L0 对话** 与 **L2 企业知识** 分存。

### 第 4 周：RAG 与引用

- [ ] **Python**：**LangChain** 检索链或 **LangGraph** 多节点：retrieve → augment → generate；**引用** 用第 2 周同类 **structured output**；**在架构描述** 中把本链路**标为 L2**。
- [ ] **Java**：`POST /ask` 入参 `question`、出参 `answer` + `citations`；**可选** 同时传 `sessionId` **仅** 用于审计/多轮，**不** 与 chunk 混库（除非有设计说明）。
- [ ] **产出**：截图或日志证明「有依据」；**Mermaid/草图** 中 **L0 vs L2** 两条**读路径**。

### 第 5 周：RAG 加深与混合检索

- [ ] **Python**：加关键词检索（BM25 或简单分词）与向量做 **hybrid**；小评测集打分；**L3 用户事实**（**选做**）：`user_memories` 小表 或 独立 collection，**仅** 存可声明的用户事实，**与 L2 文档 chunk 分 metadata 或分表**。
- [ ] **Java**：热点问句缓存、防刷；缓存 key 区分「**仅知识**」与「**用户维度**」若你做了 L3。
- [ ] **产出**：小评测表 + 改进记录；**`docs/memory-architecture.md` 草稿**（分层+谁写入谁读取）。

### 第 6 周：ReAct、Function Calling、MCP、Skills

- [ ] **Function Calling（必做）**：**Python + Java 各 1 条**「双工具」链路（**与 API 的 `tools`/`@Tool` 对齐**），**禁止**只停留在「prompt 里写 JSON 当 ReAct」作为唯一实现；**两工具** 中**建议其一** 为**记忆相关**（如 `save_user_preference` mock）**选做**。
- [ ] **ReAct（必做）**：Python 用框架 **ReAct 类 Agent** 跑通一题，**保存** 含 **action / tool / observation** 的日志；**多轮** 时**显式** 使用第 2 周 **L0** 或 **等价** 消息列表。
- [ ] **MCP（必做，最小）**：按官方**快速开始**用 **Python 或**社区模板 起一个 **MCP Server**（`stdio` 即可），**至少注册 1 个 tool**（可代理你们已有 `search`）；用 **Inspector / 官方 client** 或自写**最小 client** 调通一次 `tools/call`。
- [ ] **Skills（必做，文档级）**：在仓库建 `skills/<name>/SKILL.md`：**何时启用**、**分步**、**涉及工具名**；第 9 周可升级成「**技能路由**」**选做**。
- [ ] **产出**：1 表对比 **无工具 RAG / FC 多步 / ReAct+FC / 经 MCP 暴露**；MCP 架构**草图 1 张**；**若** 做了 L3：`save_***` 时序 **或** 数据表**截图** 一行说明。

### 第 7 周：异步与长任务

- [ ] 任选：**Python 任务队列** 或 纯 **Java + Kafka**（与你经历一致优先 Kafka）。
- [ ] **可选关联记忆**：在 `README` 或设计里**一句** 说明：哪些**异步任务** 会**更新 L2 索引** 或 **L1 摘要**（**无**实现也可，有**设计**即得分）。
- [ ] **产出**：任务状态 `PENDING / RUNNING / SUCCESS / FAIL` 与重试一次策略。

### 第 8 周：可观测与成本

- [ ] 双端统一字段：`requestId`、`model`、`inputTokens`、`outputTokens`、`latencyMs`。
- [ ] **记忆与合规（必能口述）**：**L3/对话** 中哪些字段算 **PII**；**留存**（几天）、**用户删除/导出** 在 Demo 中**怎么假实现**（如 `DELETE /me/memories` mock）；**日志** 中**不全量** 打印用户**长** 对话（**截断**策略）。
- [ ] **产出**：一次「超预算/超时」的演示与处理逻辑说明 + `docs/privacy-memory.md` **极短**（半页内）**或** 并入 `observability.md` 一节约。

### 第 9 周：综合作业（双栈合一）

- [ ] 需求建议：**企业知识库问答**：上传 Markdown/PDF，多租户可简化为多 `collection`。
- [ ] **Python 服务**（可 FastAPI）：文档解析、分块、建索引、检索、**可选**重排；**可选** 把 RAG/检索 **挂到 MCP** 上，与第 6 周 Server **合并或新起** 一个。
- [ ] **Java 服务**：用户与 API Key、**SSE 流式**、转发 Python、合并鉴权与配额（可内存模拟）；**L0**：**至少** 支持按 **session** 多轮 或 文档**说明** 无状态+取舍；**选做**：对外 **非 MCP** HTTP 或 文档说明 **MCP** 对接内测。
- [ ] **选做：Skills 路由**：`Intent → 选 Skill → 只暴露该 Skill 声明的工具子集`（可用**硬编码**映射演示）。
- [ ] **必含（记忆）**：`docs/memory-architecture.md` **定稿** 或 README 中**等长一节**：**图** + **L0/L2/（L3 未做则写原因）**；**RAG、会话** 读路径**一眼能懂**。
- [ ] **产出**：根目录 `README`：环境变量、启动顺序、`curl` 示例；若用 MCP，写清**启动顺序**与**端口/stdio**。

### 第 10 周：就业向

- [ ] 简历：项目**一段**写清「双栈：Python 侧 xx，Java 侧 xx，上线/演示形态」。
- [ ] 准备口述：**为何 Java 还学 Python** —— 生态与速度 vs 企业集成与长期维护。

---

## 五、每日时间建议

| 情况 | 建议 |
|------|------|
| 每日 **3 小时** | 1.5h Python 实验 + 1.5h Java 落地（或按周交替 2:1） |
| 每日 **6 小时** | 上午 Python 新能力，下午 Java 复现，晚上文档与补漏 |

---

## 六、避坑

1. **不要**在 **Spring AI Alibaba** 之外再并行深挖 **LangChain4j** 或另一套 **Spring AI** 样例，**以 Alibaba 官方文档与 starter 为唯一主线**；多模型/兼容端配置以**当前版本文档** 为准。
2. **不要**在向量库、框架上各换三遍；**Chroma/一种云向量** 定稿跑通第 9 周项目再考虑换。
3. **Python 与 Java 一定围绕同一套 Demo**，否则容易学成两门孤立课。
4. **ReAct 名≠必须**：有的团队只写「Tool use / Agent 循环」；**面试**时能说清**循环里**是 **多轮 Function Calling** 即可。
5. **MCP** 是**协议与边界**，不替你实现 RAG 质量；**Skills** 是**人/机可读** 的**编排层**，**不要**和「业务微服务名」混为一谈却**没有**契约文件。
6. **RAG 向量库** ≠ 用户**长期**「什么都记」：没有 **userId/tenant 隔离** 和 **写路径** 设计，**不要** 把**隐私对话** 与**制度文档** 混进**同一**检索空间而不**标注** 来源与权限。

---

## 七、推荐资料类型（随周查阅即可）

- 官方文档：**[Spring AI Alibaba](https://github.com/alibaba/spring-ai-alibaba)** 与**其基于的** Spring AI 核心概念、所选 Python 框架 Quickstart、Embedding 与 RAG 教程；依赖与 BOM 版本**以** GitHub **Release/README** 为准（仓库名/坐标若变更请自行对齐）。
- 以 **可运行仓库** 为主，少囤长视频；每周代码提交一次，便于回滚与展示。
- **ReAct 论文/综述**（**Reason+Act**）、所用模型**「Tools / function calling」** 文档、**MCP 规范与 SDK**（见周计划**流行技术索引**）。
- **记忆架构**：**短期/摘要/检索/用户事实** 分层、**Mem0 类** 产品**了解**即可（**不必** 本计划内接商业服务），详见 [`记忆架构-索引.md`](./AI应用开发学习计划-周计划/记忆架构-索引.md)。

---

## 八、与「流行」名词的快速索引

| 想搞懂 | 先读 | 在计划里练 |
|--------|------|------------|
| Function Calling / Tool use | 模型 API 的 `tools` 与**回注**多轮 | 第 1 周选做 + **第 6 周**必做 |
| ReAct | 循环=推理+观察；**日志里能** trace | **第 6 周** |
| MCP | 协议=如何**列工具**、**调工具**、**资源** | **第 6 周** Server；**第 9 周** 可选上生产形态 |
| Skills | 技能=**SOP+工具子集+触发条件** 的**声明** | **第 6 周** `SKILL.md`；**第 9 周** 路由选做 |
| **记忆架构**（L0～L4） | [`记忆架构-索引.md`](./AI应用开发学习计划-周计划/记忆架构-索引.md) | **2** L0、**3～4** L2、**5～6** L1/L3 选、**8** 合规、**9** 定稿图 |

流行技术展开：[`AI应用开发学习计划-周计划/流行技术索引-ReAct-FunctionCalling-MCP-Skills.md`](./AI应用开发学习计划-周计划/流行技术索引-ReAct-FunctionCalling-MCP-Skills.md)

---

*文档可随你进度在「周产出物」一列打勾、补充链接。祝学习顺利。*
