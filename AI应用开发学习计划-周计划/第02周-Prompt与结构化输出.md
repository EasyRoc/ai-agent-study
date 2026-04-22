# 第 2 周：Prompt 与结构化输出

> 约 **5～7 个学习日**。目标：**同一业务问题，两版 Prompt 可切换**；**JSON 输出可解析、可失败重试。**

## 本周目标

- Python：两版 System/User 模板，对比**稳定性**（用简单脚本各跑 5 次看解析成功率）。
- Java：Prompt 外置到 **YAML 或 `resources/prompts/*.txt`**，统一 **解析层**；对 JSON 解析失败**重试 1 次**（可换温度或加一句“只输出 JSON”）。
- **记忆架构 L0 / L1**（与 [`记忆架构-索引`](./记忆架构-索引.md) 对齐）：在**聊天/类聊天** 接口中引入 **`sessionId`**，仅把「**滑窗**后的历史」或 **「旧轮摘要 + 最近轮」** 拼进请求；在 `README` 或 `docs/memory-l0-l1.md` 写清**截断规则**（**必做** L0；L1 **选做**）。

## 业务场景（建议二选一，贯穿全周）

- **A**：从用户自然语言中抽取 `intent`, `slots`（如「订会议室下午三点」→ JSON）。
- **B**：对一段客服对话打标签：`emotion`, `need_human` 布尔, `summary`。

可虚构数据，不追求真实效果，**追求可解析**。

## 按日计划

### 第 1 天：Prompt 版本 v1

- [ ] 写 v1 中英均可：明确要求「只输出 JSON，不要 markdown 代码块」。
- [ ] Python：函数 `run_structured(instruction) -> dict`，**json.loads** 前 strip fence。
- [ ] 记录：5 次中失败次数；失败样例 1 条保存到 `notes/failures.md`。

### 第 2 天：Prompt 版本 v2 + 对比

- [ ] 写 v2：增加 2～3 个 **one-shot 示例**（样例入参 + 样例 JSON 输出）。
- [ ] 同样跑 5 次，和 v1 填表对比：成功率、平均输出长度。

### 第 3 天：JSON Schema / 严格模式（视模型支持）

- [ ] 若你的模型支持 `json_schema` 或 `response_format`：**开启** 并对比开启前后。
- [ ] 若不支持：用 **Pydantic** 在 Python 侧校验字段，不合法则重试并附带「上次错误是 xxx」。

### 第 4 天：Java 外置与加载

- [ ] 将 v2 的 system 部分放到 `src/main/resources/prompts/xxx.txt`。
- [ ] 启动时加载；支持 **Spring Profile** 切换 `v1`/`v2`（`application-v1.yml` 等）。

### 第 5 天：Java 解析与重试

- [ ] `StructuredChatService`：`call() -> 解析 Jackson -> 失败则 retryOnce()`。
- [ ] 重试时 prompt 可追加：「你上次输出了非 JSON，请严格只输出 JSON」。
- [ ] 单元测试：mock 模型先返回坏字符串再返回好 JSON（可手工 stub）。

### 第 6 天：与第 1 周接口结合

- [ ] 新增 `POST /api/v1/structure`，body 为 `{ "raw": "用户输入" }`，返回 `parsed` + `version` 字段。
- [ ] Python 保留脚本版用于对比，**不强制**和 Java 同端口。

### 第 7 天：错例整理

- [ ] 整理 **3 个** 失败样例 + **改法**（更短 system / 更强约束 / 换模型）。
- [ ] 更新 `README`「第2周」小节：如何切换 prompt 版本。

## 周产出物

- [ ] `failures` 或笔记中 3 错例 + 改法。
- [ ] 双端各 1 个**可运行**的「结构化」入口（脚本是其一）。

## 完成标准

- 同一输入，v2 的 JSON **可解析率** 不低于 v1（或说明模型限制并给出替代方案）。

## 与第 3 周衔接

第 3 周要把「一段段文本」向量化，本周的「结构化」可用于 **metadata**（如标签过滤检索）。

## 选做

- 在日志里**禁止**打印完整 user 文本（脱敏/截断 100 字），为第 8 周铺垫。
