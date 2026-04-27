# 第 2 周：解析 / 结构化失败样例与改法

> 与课表「错例整理」对应；请结合本机 5 次小实验与 Java `/api/v1/structure` 实跑，把**真实**失败填进来。

1. **现象**：（例）模型在 JSON 外多写了一句「好的」→ 早期若用手写 `json.loads` 易失败。  
   **改法**：改用 **LangChain `with_structured_output`** 或 **Java `ChatClient#entity`**（Structured Output），由框架合成分辨。

2. **现象**：（例）`slots` 里出现数字/嵌套，与 `Map<String,String>` 或 Pydantic 字段类型不一致。  
   **改法**：收紧 schema（全改为字符串）或在 Prompt 中写明「槽位值一律用字符串表示」。

3. **现象**：（例）多轮时旧轮 user 被截断后，模型丢失指代。  
   **改法**：适当增大 L0 滑窗条数、或上 L1 摘要（第 2 周选做）保留更早语义。

---

*脚本 `scripts/week02_structured_intent.py` 跑满 5 次若未全成功，请把**一条** `stderr`/异常信息贴到上表「现象」中。*
