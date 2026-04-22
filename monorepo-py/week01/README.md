# 第 1 周（大模型应用地图与 API）

与周计划 [`第01周-大模型应用地图与API设计.md`](../../AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md) 同步；代码均在 `monorepo-py/scripts/`。

| 天次 | 脚本 / 说明 |
|------|-------------|
| 第 1 天 | [`scripts/week01_day1_sync_chat.py`](../scripts/week01_day1_sync_chat.py) — 同步 `chat()`、三档超时、耗时与字符数 |
| 第 2 天 | [`scripts/week01_day2_stream_chat.py`](../scripts/week01_day2_stream_chat.py) — 流式 `stream_chat()`、首段延迟（TTFT）、`week01/day2_首token自测.md` 自动追加大致 ms |
| 第 6 天 | 时序图 + 联调：Mermaid 与根 [`README` 双端各一条命令](../../README.md#week1-acceptance)；[周计划第6天](../../AI应用开发学习计划-周计划/第01周-大模型应用地图与API设计.md#week1-day6) |
| 第 7 天 | 本周收尾 + **Function Calling**：[`day7_本周收尾与FC.md`](./day7_本周收尾与FC.md) · 脚本 [`scripts/fc_min.py`](../scripts/fc_min.py)（`messages` 手搓多轮；通义建议 `qwen-plus`） |

环境同第 0 周：`conda` + `pip install -r requirements.txt` + `monorepo-py/.env`（或 `export` 密钥）。
