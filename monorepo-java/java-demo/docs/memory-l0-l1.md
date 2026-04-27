# 第 2 周：L0 / L1 记忆与 `/api/v1/structure` 的对应关系

| 模式 | 行为 |
|------|------|
| **无 sessionId** | 每次请求在服务端**新建** `sessionId`（UUID），响应体里返回，便于客户端多轮时作为 **threadId** 带回。 |
| **L0（必做，本 Demo）** | 使用 **checkpointer**：`com.alibaba.cloud.ai.graph.checkpoint.savers.MemorySaver`（内存实现；生产可换 `RedisSaver` 等，见 [java2ai 短期记忆](https://java2ai.com/docs/frameworks/agent-framework/tutorials/memory)）。会话隔离键为 `RunnableConfig#threadId`，与请求体中的 `sessionId`**一致**。 |
| **滑窗** | 进模型前由 `StructureL0TrimmingHook`（`MessagesModelHook`）按 **`app.structure.l0.max-messages`** 裁剪 `messages` 列表，避免上下文无限增长。 |
| **L1（选做）** | 多轮极长时，将更早内容**压成 summary** 再与近轮**合并**进上下文。本 `java-demo` 未实现 L1 调用链，仅在本表说明口径。 |

**实现要点**：`ReactAgent.call(userText, config)` 会在图状态里**累积**多轮；checkpointer 按 `threadId` 持久化 checkpoint；**不是**手写 `ConcurrentHashMap<String, List>`。

**与 RAG 关系**：L2 是企业知识/文档检索；L0 只是**多轮 API 的短期上下文**，二者**不要**混库。
