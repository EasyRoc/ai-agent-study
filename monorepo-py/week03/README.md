# 第 3 周：Embedding、Milvus、检索 API

> 与 [`../../AI应用开发学习计划-周计划/第03周-Embedding与向量检索.md`](../../AI应用开发学习计划-周计划/第03周-Embedding与向量检索.md) 对齐。本目录为 **L2 外显/检索记忆**（组织/制度知识），**不是** 第 2 周 L0 会话。

向量库为 **Milvus**（[LangChain `langchain_milvus`](https://python.langchain.com/docs/integrations/vectorstores/milvus)）。本地默认使用 **Milvus Lite** 单文件 `data/milvus_lite.db`（macOS / Linux 常见环境），无需 Docker。若与线上一致，可设环境变量改连 **Milvus Standalone**（如 `MILVUS_URI=http://127.0.0.1:19530`）或 Zilliz Cloud。

**Windows**：`milvus-lite` 安装可能失败，请用 Docker 起 Milvus 并设 `MILVUS_URI` 指向其地址，见 [Milvus 安装文档](https://milvus.io/docs/install_standalone-docker.md)。

## 依赖与密钥

在 `monorepo-py` 下：

```bash
pip install -r requirements.txt
# 与前几周相同：DASHSCOPE_API_KEY；可选 EMBEDDING_MODEL（默认 text-embedding-v2）
```

若仍报 `milvus-lite is required for local database connections` 或 `ImportError: ... milvus_lite`：

1. 确认在**你运行 Python 的同一个环境**里安装（`which python` 与 `which pip` 应指向同 env）。  
2. 执行（**务必带上 setuptools 上界**，否则易踩 `No module named 'pkg_resources'`，`milvus-lite` 仍依赖它）：  
   `pip install -U "pymilvus[milvus_lite]>=2.4.2" "milvus-lite>=2.4.0" "setuptools>=69,<81"`  
3. 验证（必须通过）：  
   `python -c "from milvus_lite.server_manager import server_manager_instance"`  
4. 若第 2 步在 **Python 3.13** 下报「找不到轮子 / 无法编译」：多为 **milvus-lite 尚未支持该小版本**；可 **新建 Python 3.10～3.12 的 venv/conda 环境**再装，或**不用 Lite 文件**、起 Docker 版 Milvus 后设：  
   `export MILVUS_URI=http://127.0.0.1:19530`  
   与[官方用 `MilvusClient("./xxx.db")` 的示例](https://milvus.io/docs/milvus_lite.md)相比，本仓库用 LangChain 的 `langchain_milvus`，底层仍是 `MilvusClient(**connection_args)`；**连本地 `.db` 的前提同样是 `milvus_lite` 能成功 import。**

**Embedding 维数**以你账号下实际 API 返回为准；`text-embedding-v2` 常见为 1024 维（请在首次 `/embed` 或 ingest 输出中确认）。

## Milvus 连接（`.env` 可选）

| 变量 | 说明 |
|------|------|
| （未设置时） | 使用 `data/milvus_lite.db`（自动创建父目录） |
| `MILVUS_URI` | 如 `http://127.0.0.1:19530`、Zilliz HTTPS 地址、或本机 `*.db` 文件路径（Lite） |
| `MILVUS_HOST` + `MILVUS_PORT` | 与 `MILVUS_URI` 二选一；未设 `MILVUS_URI` 时用于连接 Standalone |
| `MILVUS_TOKEN` / `MILVUS_USER`+`MILVUS_PASSWORD` | 云或开启认证的集群 |

`collection` 名固定为 **`week03_hr`**（与 `week03/milvus_settings.py` 中 `COLLECTION_NAME` 一致）。

## 一键入库

```bash
cd monorepo-py
./week03/ingest.sh
# 或：python3 -m week03.ingest
```

语料：`../data/corpus.txt`（每行一条制度/说明类短文本）。入库脚本内 **`drop_old=True`**，会删除已存在的同名 collection 后重建（数据幂等可复现）。

## 启动向量 HTTP 服务

默认 **8010** 端口（与 `java-demo` 的 `app.vector.base-url` 一致）：

```bash
cd monorepo-py
python3 -m uvicorn week03.api:app --host 0.0.0.0 --port 8010
```

### 断点调试 `/search`、以及「总是空 results」

- **PyCharm**：**Run — Edit Configurations** → **+ Python** 不要用「脚本路径」，用 **Module name** `uvicorn`，**Parameters** `week03.api:app --host 0.0.0.0 --port 8010`（**先不要**加 `--reload`，否则子进程里断点常不命中）。**Working directory** 选 **`monorepo-py` 根目录**。在 `week03/api.py` 的 `search()` 里下断点，用 **Debug** 启动。
- **`/search` 遇错仍返回 200 + 空 `results`（课表设计）**，异常被吃掉时终端默认看不见。已改为记录 **`logger.exception(...)`**；起服务时加 `--log-level debug` 或至少默认 INFO 也能看到 ERROR 级栈。若希望**直接抛给客户端**调接口：  
  `export WEEK03_SEARCH_RAISE=1` 再启 uvicorn，便于在 Postman/浏览器里看到 500 与具体原因。
- 先确认 **`GET /health`** 里 `ingested: true`；为 `false` 时不会命中数据，多搜也是空。
- 若 `/search` 在构造 `Milvus` 时即失败：多为 **库已有数据** 时 LangChain 在 `__init__` 里就要连 ORM，本仓已用 **`prime_orm_connection_before_langchain_milvus()`** 在 `Milvus()` 前补好 `connections`（在旧代码里只会在 `Milvus()` 后注册，为时已晚）。

## 如何连接并查看数据（与「SQL 里 SELECT」类似的心智模型）

- **Milvus Lite** 的数据在本地文件 `data/milvus_lite.db`（**不是** MySQL/Redis，没有通用 GUI 的「用账号密码连 .db 文件」这一说）。查看方式是用 **pymilvus 的 `MilvusClient` 连和 ingest 一样的 URI**（见 `connection_args()`），对 **collection** `week03_hr` 做 `describe` / `get` / `query`。
- **本仓库提供脚本**（ingest 之后执行）：

```bash
cd monorepo-py
python -m week03.peek_milvus
```

会打印集合 schema、行数、并用主键 `chunk-0`… 拉几行文本/向量维信息。

- **若使用独立 Milvus**（`http://127.0.0.1:19530` 等），可用开源可视化 **[Attu](https://github.com/zilliztech/attu)** 或 Zilliz Cloud 控制台，连到**同一 gRPC/HTTP 地址**即可浏览；**Lite 的 `.db` 文件**一般仍用 Python 客户端最省事。

- **和官方示例的关系**：`MilvusClient("./milvus_demo.db")` 与我们在 `connection_args()` 里写的 **本地文件 URI 是同一类连接**；`peek_milvus` 多封装了一步「打印 `week03_hr` 里有什么」。

### 用 DataGrip / IDE 直接打开 `milvus_lite.db` 的常见问题

1. **`data` 是乱码吗？**  
   不是 UTF-8 文本坏了。Lite 在 SQLite 里用 **`BLOB`** 存一行的**二进制序列化**（元数据、文本、向量等打包在一起），IDE 当「字符串」显示时，**前面会是一堆不可见/怪字符**，中间或后面可能能看到中文片段。这属于**用关系型工具看向量引擎内部存盘格式**的正常现象。要看结构化字段请用 **`python -m week03.peek_milvus`** 或 `MilvusClient.get` / `query`，不要依赖直接 `SELECT` 理解语义。

2. **为什么只有 `id` / `milvus_id` / `data` 三列，没有「向量列」？**  
   在 **Milvus 逻辑模型**里，LangChain 建库时已有 **`vector` 浮点向量场**和 **`text` 等字段**（可用 `describe_collection` 或 `peek_milvus` 看 schema）。**物理上** Milvus Lite 用 SQLite 做嵌入存储，**不必**、也不会按「一列 = float 数组」展开成你熟悉的宽表。  
   若你**需要单独一列看向量**，那是 **Milvus 的 schema 里本来就有**（`describe_collection` 里可见），**不是**再往 SQLite 里手加一列；业务上检索仍走 **`POST /search`** 的向量近邻，无需改 SQLite 文件结构。

## 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 能否连上 Milvus、且存在 collection `week03_hr`（已 ingest） |
| POST | `/search` | Body: `{"q":"...","k":3}` → `results[]` 含 `id`,`text`,`score` |
| POST | `/embed` | Body: `{"text":"..."}` → 返回 `dimension`、`model`（不返回全向量，防刷屏） |

## 与 Java 联调

1. 先 `ingest` + 起 uvicorn。  
2. 起 `monorepo-java/java-demo`（或设 `APP_VECTOR_BASE_URL` 指向你的 Python 地址）。  
3. 访问 `GET /api/v1/vector-demo?q=报销`（本仓库将该路径列入鉴权白名单，便于本机试）。

更多 `curl` 见 [`../notes/search-samples.md`](../notes/search-samples.md)。
