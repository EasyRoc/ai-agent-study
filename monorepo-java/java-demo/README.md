# java-demo（第 0 周起）

## 做什么

- Spring Boot **3.5.x** + **Spring AI Alibaba**：`spring-ai-alibaba-starter-dashscope` + **`spring-ai-alibaba-agent-framework`**（版本由父 POM 的 **`spring-ai-alibaba-bom`** + **`spring-ai-alibaba-extensions-bom`** 与 **`spring-ai-bom`** 对齐；在 `monorepo-java/pom.xml` 集中管理）
- `GET /api/v1/health/llm`：探活，向通义发「你好」，`preview` 为前 200 字（与 `monorepo-py/scripts/health_chat.py` 对齐）
- **第 1 周第 3 天**：`POST /api/v1/chat` —— 同步多轮/单条对话
- **第 1 周第 4 天**：`POST/GET /api/v1/chat/stream` —— **SSE**（`text/event-stream`）流式；`ChatClient` 的 `stream().content()`（Reactor `Flux`）**直连**通义，与上项共用同一 `application.yml` 中的 <code>spring.ai.dashscope</code>（<code>api-key</code>、<code>model</code> 等）  
- **第 1 周第 5 天**：业务接口需请求头 **`X-API-Key: demo`**（占位，可用环境变量 `APP_EXPECTED_API_KEY` 覆盖）；**不**带或值错误 → `401` + `{"code":"UNAUTHORIZED",...}`。探活 **`/api/v1/health/**`** 与 Spring **`/error`** 不在此列（与 `make health-java` 兼容）。**内存**按 **客户端 IP**（先 `X-Forwarded-For` 首段）做滑动窗口 **每分钟 30 次**（`app.rate-limit.*`，可关；多节点**不**共享，生产应换统一网关/Redis 限流）。  
- **实现约定**：`ChatClient` + DashScope 自动配置，**不**另写 <code>RestClient</code> 作第二套；若你需旁路实验，在分支里注明，勿与主路径长期并存。

以下凡调用「对话类」接口的 `curl` 均带 **`-H 'X-API-Key: demo'`**；`GET /api/v1/health/**` 探活**无需**此头（与 `make health-java` 一致）。

- **第 1 周第 6 天**（时序图 + 联调）：Mermaid 图与**双端各一条**命令在仓库 [根 `README`「第1周联调与验收」](../../../README.md#week1-acceptance)；时序与「直连/网关」图亦在周计划 [第 01 周第 6 天](../../../AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md#week1-day6)。
- **第 1 周第 7 天**（收尾 + **Function Calling**）：`POST /api/v1/fc/chat`；`Week01DemoTools`（`add_numbers` / `server_time_iso`）+ `ToolCallingChatOptions` + 框架内工具执行；Python 对照见 [`monorepo-py/scripts/fc_min.py`](../../../monorepo-py/scripts/fc_min.py)。通义请优先 **`qwen-plus`**（`spring.ai.dashscope.chat.options.model` 或 `LLM_MODEL`）。
- **第 2 周**（**Structured Output** + L0 + 外置 Prompt）  
  - **主路径**：`StructureExtractionService` 使用 **`ReactAgent`** + **`outputType(IntentSlotsResult.class)`**，返回的 `AssistantMessage` 再反序列化为强类型；多轮由 [**MemorySaver** checkpointer](https://java2ai.com/docs/frameworks/agent-framework/tutorials/memory) + **`RunnableConfig.threadId` / 请求体 `sessionId`** 维护，**非**手写 `ConcurrentHashMap`。  
  - **滑窗**：`StructureL0TrimmingHook`（`MessagesModelHook`）在进模型前按 **`app.structure.l0.max-messages`** 裁剪 `messages`。  
  - **L0**：`POST /api/v1/structure` 可带 `sessionId`；不带则响应里返回新 id（作 **threadId**）。说明见 [`docs/memory-l0-l1.md`](./docs/memory-l0-l1.md)。  
  - **Prompt**：`src/main/resources/prompts/structure-v1.txt` / `structure-v2.txt`，由 `app.structure.prompt-version` 选择。切换：① `export SPRING_PROFILES_ACTIVE=v2`；② `export APP_STRUCTURE_PROMPT_VERSION=v2`。  
  - **依赖坐标**（版本由父 BOM 管理）：`spring-ai-alibaba-starter-dashscope`、`spring-ai-alibaba-agent-framework`（内含 **graph-core** + `MemorySaver`）。

### 第 2 周：`POST /api/v1/structure`（JSON）

- **Request**：`{ "raw": "用户说法", "sessionId": "可选" }`  
- **Response**：`{ "parsed": { "intent": "...", "slots": { ... } }, "promptVersion": "v1", "sessionId": "...", "historyMessageCount": N }`  
- **错误**：解析/上游失败时 `502` + 课表统一 `ApiErrorResponse` 风格（由 `GlobalExceptionHandler` / 网关层处理，与第 1 周一致即可）。

```bash
# 单轮：不传 sessionId
curl -s -X POST http://localhost:8080/api/v1/structure \
  -H 'X-API-Key: demo' \
  -H 'Content-Type: application/json' \
  -d '{"raw":"帮我订周一下午三点的会议室 301"}' | jq .

# 多轮：用返回的 sessionId 再发一轮
# curl ... -d '{"raw":"改到四点","sessionId":"<上次的 sessionId>"}' | jq .
```

### 第 3 周：向量检索网关（`WebClient` → Python `POST /search`）

- **配置**：`app.vector.base-url`（默认 `http://127.0.0.1:8010`），可用环境变量 `APP_VECTOR_BASE_URL` 覆盖；超时 `connect-timeout-ms` / `read-timeout-ms` 各 **5000**（与课表一致）。  
- **实现**：`VectorServiceClient` + `spring-boot-starter-webflux` 的 `WebClient`；Python 未启动或超时时 **502**，`reason` 以 `VECTOR_TIMEOUT` 开头时 JSON `code` 为 **`VECTOR_TIMEOUT`**。  
- **鉴权**：`GET /api/v1/vector-demo` 已加入 `app.security.public-paths`（本机演示；生产请收敛）。  
- **先决条件**：在 `monorepo-py` 完成 **Milvus** 入库（`week03/ingest.sh`，默认 Milvus Lite 文件 `data/milvus_lite.db`）并启动 `uvicorn week03.api:app --port 8010`，见 [`monorepo-py/week03/README.md`](../../../monorepo-py/week03/README.md)。

```bash
# 需 Python 向量服务已监听 8010 且已 ingest
curl -s "http://localhost:8080/api/v1/vector-demo?q=报销流程&k=3" | jq .
```

## 环境

- JDK **17+**
- Maven 3.9+（或 IDE 自带）

## 密钥（不要写进 yml）

任选其一（与 `application.yml` 中占位一致）：

```bash
export AI_DASHSCOPE_API_KEY="你的灵积/DashScope Key"
# 或与 Python 共用：
export DASHSCOPE_API_KEY="同上"
```

## 运行

```bash
cd monorepo-java/java-demo
mvn spring-boot:run
```

另开终端：

```bash
curl -s http://localhost:8080/api/v1/health/llm
```

成功时类似：`{"ok":true,"preview":"你好！有什么...","length":123}`；若未配 key 或网络问题，`ok` 为 `false` 且 HTTP 503。

### 第 1 周第 3 天：`POST /api/v1/chat`（JSON）

- **Request**：`messages` 与 `prompt` **二选一**（不要同时传）
  - 仅 `prompt`：单轮，等价于一条 `user` 消息
  - 仅 `messages`：`role` 为 `system` / `user` / `assistant` 之一的多轮
- **Response**：`{ "content": "...", "model": "qwen-turbo" }`（`model` 与 `application.yml` 中配置一致）
- **错误**（`4xx/5xx`）：`{ "code": "VALIDATION_ERROR" | "LLM_UPSTREAM" | ... , "message": "..." }`，不直接返回 API Key

`prompt` 示例：

```bash
curl -s -X POST http://localhost:8080/api/v1/chat \
  -H 'X-API-Key: demo' \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"用一句话解释什么是大模型流式输出"}' | jq .
```

`messages` 多轮示例：

```bash
curl -s -X POST http://localhost:8080/api/v1/chat \
  -H 'X-API-Key: demo' \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"说你好"}]}' | jq .
```

校验失败示例（`400` + `code` + `message`；需**先**能过鉴权，故仍带头）：

```bash
curl -s -i -X POST http://localhost:8080/api/v1/chat \
  -H 'X-API-Key: demo' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

### 第 1 周第 4 天：SSE 流式 `GET` / `POST /api/v1/chat/stream`

- **与同步共用配置**：`spring.ai.dashscope`（密钥、<code>spring.ai.dashscope.chat.options.model</code> 等），**无**第二套 <code>baseUrl</code>
- **技术路径**：<code>ChatLlmService#streamContent</code> → `ChatClient#stream#content` → <code>Flux</code> → 控制器内写入 <code>SseEmitter</code>（<code>MediaType.TEXT_EVENT_STREAM</code>）
- **事件名**（可配合浏览器 DevTools 或 <code>curl -N</code> 观察）  
  - <code>meta</code>：首包，JSON，含 <code>model</code>  
  - <code>delta</code>：正文增量（可多条）  
  - <code>done</code>：正常结束，数据为 <code>[DONE]</code>  
  - <code>error</code>：失败时，JSON 含 <code>code</code> / <code>message</code>（与同步接口**同样不泄露**密钥）

`curl` 连续看流（<strong>勿</strong>用无 <code>-N</code> 的缓冲，否则要很久才出字）：

```bash
# POST：请求体与 /chat 相同（二选一：prompt 或 messages）
curl -N -s -X POST http://localhost:8080/api/v1/chat/stream \
  -H 'X-API-Key: demo' \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"用三句话介绍你自己"}'
```

单轮、便于浏览器 <code>EventSource</code> 或 <code>curl -N</code>（<strong>请对 query 中中文做 URL 编码</strong>，或先在终端里用短英文测）：

```bash
curl -N -s -H 'X-API-Key: demo' "http://localhost:8080/api/v1/chat/stream?prompt=Hi"
```

`prompt` 为空或缺失时返回 <code>400</code>（与同步类同的 <code>ApiErrorResponse</code>，非 SSE 体；若已建立长连接后的模型错误，则通过 SSE 的 <code>event: error</code> 返回）。

### 第 1 周第 5 天：鉴权与限流（`X-API-Key` + 按 IP 每分钟 30 次，可配）

- **401**：`curl` 未带、或 `X-API-Key` ≠ 当前 `app.security.expected-api-key`（默认 `demo`；可用 `export APP_EXPECTED_API_KEY=...` 覆盖，勿提交仓库）
- **429**：同 IP 在 60s 内请求次数超过 `app.rate-limit.per-minute`（**不含**被白名单放行的 `health`）；关限流可设 `app.rate-limit.enabled: false`（`application.yml` 或等效环境变量，见 Spring Boot  relaxed binding）
- 浏览器**原生** `EventSource` **不能** 设置任意请求头，若直连接口需鉴权，一般依赖**同源**反代在网关**注入** `X-API-Key`，或前端用 **`fetch` + `POST` `/chat/stream`** 读流。本课表验收以 **`curl` 带 `-H 'X-API-Key: demo'`**（`GET/POST` 的 `/chat/stream` 同理）为主。

**鉴权与限流自测**：

```bash
# 应返回 401 与 UNAUTHORIZED
curl -s -i -X POST http://localhost:8080/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"a"}' | head -20
```

### 第 1 周第 7 天：`POST /api/v1/fc/chat`（Function Calling）

- **Body**：`{ "prompt": "把 3 和 9 加起来" }` 或问当前时间（模型会选用已注册工具）。
- **Response**：`{ "content": "...", "model": "..." }`，错误体同第 3 天 `ApiErrorResponse`。
- **实现**：`com.aimodel.javademo.tools.Week01DemoTools`（`@Tool`）、`FunctionCallingChatService`（`internalToolExecutionEnabled(true)`）。与 Python `fc_min.py` **手搓 messages** 不同，Java 侧由 Spring AI 在**一次**模型调用链路内完成工具往返（便于对照学习两种集成方式）。

```bash
curl -s -X POST http://localhost:8080/api/v1/fc/chat \
  -H 'X-API-Key: demo' \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"计算 3.5 加 4.5，用工具"}' | jq .
```

若返回 502 且日志提示工具/模型不兼容，请将 `application.yml` 中模型改为 **`qwen-plus`** 或在控制台确认当前模型支持 **tools**。

## 版本说明

- `pom.xml` 里 `spring-ai-alibaba.version` 与 **BOM/官方示例** 对齐；升级请到 [Spring AI Alibaba](https://github.com/alibaba/spring-ai-alibaba) 与 [java2ai 文档](https://java2ai.com) 核对 **Spring Boot** 与 **starter** 兼容表后，**只改版本号**再 `mvn clean compile`。
