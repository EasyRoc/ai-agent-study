# 第 2 周：Prompt 与结构化输出

> 约 **5～7 个学习日**。目标：**同一业务问题，两版 Prompt 可切换**；**结构化结果以框架/模型能力为主**（**Structured Output**），手写 `json.loads` + 字符串修复为**对照或兜底**；**L0 / L1** 记忆与第 1 周接口自然衔接。

## 技术基线（从本周起默认）

- **Java**：**Spring Boot 3.5.x** + **双 BOM**：父 POM 同时 **`import`** **`spring-ai-alibaba-bom`**（含 `agent-framework` 等）与 **`spring-ai-alibaba-extensions-bom`**（管理 **`spring-ai-alibaba-starter-dashscope`** 等扩展，与[官方根工程](https://github.com/alibaba/spring-ai-alibaba)一致）；子模块**至少**依赖：  
  `com.alibaba.cloud.ai:spring-ai-alibaba-starter-dashscope`、`com.alibaba.cloud.ai:spring-ai-alibaba-agent-framework`。  
  结构化输出：**优先** 使用 **Spring AI 的 Structured Output**（如 `ChatClient` 绑定 **Bean / 强类型 DTO**、或官方文档中与通义/DashScope 搭配的 **JSON Schema / 响应格式** 能力），**不要**把「纯字符串 + Jackson 硬解析 + 重试」当作唯一主路径。
- **Python**：**优先** 使用 **LangChain**（如 `with_structured_output`、Pydantic / `TypedDict`）或 **LangGraph** 中提供的节点与状态机能力；直连 `openai` SDK 仅作**对照**或厂商特殊能力实验。

## 本周目标

- Python：两版 System/User 模板，用 **LangChain 结构化输出** 各跑多次，记录**解析成功率**与**失败样例**（可仍写入 `notes/failures.md`）。
- Java：Prompt 外置到 **YAML 或 `resources/prompts/*.txt`**；用 **Structured Output → 强类型对象** 接收结果；若有必要，再对**极少数**坏输出做**一次**补救提示或重试（**明确标注**为兜底路径）。
- **记忆架构 L0 / L1**（与 [`记忆架构-索引`](./记忆架构-索引.md) 对齐）：在**聊天/类聊天** 接口中引入 **`sessionId`**，仅把「**滑窗**后的历史」或 **「旧轮摘要 + 最近轮」** 拼进请求；在 `README` 或 `docs/memory-l0-l1.md` 写清**截断规则**（**必做** L0；L1 **选做**）。

## 业务场景（建议二选一，贯穿全周）

- **A**：从用户自然语言中抽取 `intent`, `slots`（如「订会议室下午三点」→ 结构化结果）。
- **B**：对一段客服对话打标签：`emotion`, `need_human` 布尔, `summary`。

可虚构数据，不追求真实效果，**追求类型稳定、可验收**。

## 按日计划（已按「框架优先」重排）

### 第 1 天：栈与契约

- [ ] **父 POM**：`spring-ai-alibaba-bom` + **`spring-ai-alibaba-extensions-bom`** + `spring-ai-bom` 与 **Spring Boot** 三边版本对齐；`java-demo` 已含 **`spring-ai-alibaba-starter-dashscope`** 与 **`spring-ai-alibaba-agent-framework`**（无则补上）。
- [ ] 读**官方文档**：Spring AI **Structured Output**、DashScope/通义侧若支持 **JSON/Schema** 时的配置键名；Python 装 **`langchain`** 及你选用的 chat 模型集成包（如 `langchain-openai` 或社区里的兼容适配），并跑通**最小**一次「返回 Pydantic 模型」。
- [ ] 在笔记写清：**本周主验收** = 「框架绑定类型」**成功**，而非「能 regex 出 JSON」。

### 第 2 天：Python — 两版 Prompt + LangChain 结构化

- [ ] 写 v1、v2 两版 system/user（v2 含 2～3 个 one-shot 示例更稳）。
- [ ] 用 **LangChain** 的 **structured output**（或等价 API）将模型输出**直接**映射到你的 **Pydantic 模型**；对同一输入各跑 5 次，填表：成功率、平均延迟（可选）、失败样例 1 条进 `notes/failures.md`。

### 第 3 天：Java — Structured Output 主路径

- [ ] 为场景 **A 或 B** 定义 **Java 记录类/DTO**（或 Spring AI 文档推荐的方式）作为 **输出类型**。
- [ ] 使用 **`ChatClient`（或当前版本推荐的构建器）+ Structured Output**，使模型结果**反序列化为该类型**；**若** 官方提供基于 **JSON Schema** 的选项，在 `application.yml` 或代码中**显式打开**并记录差异。
- [ ] **对比笔记**：与「`String` + Jackson」相比，**省掉**了哪些易错点（**markdown  fence**、多余解释文本等）？

### 第 4 天：Prompt 外置 + Profile

- [ ] 将**定稿的** system 模板放到 `src/main/resources/prompts/xxx.txt`（或按你们规范拆分多文件）。
- [ ] 支持 **Spring Profile** 切换 v1 / v2（`application-v1.yml` 等或 `@Profile` Bean）。
- [ ] 确认：**结构化类型定义** 与 Prompt 中字段**一致**（改字段时**同时**改 DTO，避免「口头 JSON」与类型脱节）。

### 第 5 天：L0 会话 + 接口

- [ ] 为「类聊天/结构化」入口增加 **`sessionId`**：内存 `ConcurrentHashMap` 或等价；只携带**滑窗**内 `messages` 再调用模型/Structured Output。
- [ ] 新增或对齐 **`POST /api/v1/structure`**：`{ "raw": "..." }`（可带 `sessionId`）→ 返回 **`parsed`（强类型序列化）+ `promptVersion`**；Python 侧**可**保留脚本对照，不强制同端口。

### 第 6 天：兜底策略与单测

- [ ] **仅当** 主路径极偶发失败时：补**一次**重试或**一句**「请只输出与 schema 一致的内容」（写清**触发条件**）；在单元测试里用 **mock** 模拟**一次**坏串再**一次**好输出（**证明**兜底存在即可）。
- [ ] **L1（选做）**：轮数超阈值时生成 `summary` 再与近轮**合并**进上下文（伪代码或真实现均可）。

### 第 7 天：错例整理与文档

- [ ] 整理 **3 个** 失败样例 + **改法**（更短 system / 更强约束 / 换模型 / **收紧 schema**）。
- [ ] 更新子工程 `README`「第 2 周」：**依赖坐标**、**如何切换** Profile、**L0 截断规则** 一句话。

## 周产出物

- [ ] `failures` 或笔记中 3 错例 + 改法（可与第 1、2 天合并）。
- [ ] 双端各 1 个**可运行**的「**类型化**结构化」入口；Java 端代码中**能指出**哪几处是 **Structured Output**、哪处是**兜底**。

## 完成标准

- 能演示：**v2 在成功率或类型安全上** 不低于 v1，或**说明模型/API 限制**并给出**经文档佐证的**替代方案（例如仅部分模型支持 schema）。

## 与第 3 周衔接

第 3 周要把「一段段文本」向量化，本周的「结构化」结果可用于 **metadata**（如标签过滤检索）。

## 选做

- 在日志里**禁止**打印完整 user 文本（脱敏/截断 100 字），为第 8 周铺垫。
