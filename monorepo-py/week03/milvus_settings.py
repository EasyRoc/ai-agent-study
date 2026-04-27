"""
第 3 周：Milvus 连接参数与 collection 名（ingest、api 共用）。

默认使用本地 **Milvus Lite** 文件 `data/milvus_lite.db`（无需 Docker；Windows 需改用远程 URI，见 README）。
若已部署 Milvus Standalone，可设 MILVUS_URI 或 MILVUS_HOST。
"""
from __future__ import annotations

import os
import sys
# pathlib：跨平台路径；`/` 运算符可拼接路径，类似 Path.resolve() 的链式感，比写死 "foo/bar" 更稳
from pathlib import Path
from typing import Any

# __file__ 当前文件路径；parent.parent 即 monorepo-py 根（与 Java 里从 Class 处反推包路径一个意思）
_ROOT = Path(__file__).resolve().parent.parent
# Milvus 的「表名 / 逻辑集合」；和 MySQL 的 table、ES 的 index 可类比
COLLECTION_NAME = "week03_hr"
_DEFAULT_LITE_PATH = _ROOT / "data" / "milvus_lite.db"


def connection_args() -> dict[str, Any]:
    """
    与 langchain_milvus、pymilvus **MilvusClient** 兼容的参数字典（优先 `uri`，与官方客户端一致）。

    返回的 dict 会原样用于 ** MilvusClient(**connection_args()) **：
    在 Java 里相当于把 `Map<String, Object>` 展成具名参数（Python 的「字典解包」）。
    """
    uri = os.environ.get("MILVUS_URI", "").strip()
    host = os.environ.get("MILVUS_HOST", "").strip()
    if uri:
        d: dict[str, Any] = {"uri": uri}
    elif host:
        port = os.environ.get("MILVUS_PORT", "19530").strip()
        d = {"uri": f"http://{host}:{port}"}
    else:
        _DEFAULT_LITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        d = {"uri": str(_DEFAULT_LITE_PATH)}
    token = os.environ.get("MILVUS_TOKEN", "").strip()
    if token and "token" not in d:
        d["token"] = token
    user = os.environ.get("MILVUS_USER", "").strip()
    password = os.environ.get("MILVUS_PASSWORD", "").strip()
    if user and password and "user" not in d:
        d["user"] = user
        d["password"] = password
    return d


def _register_orm_if_missing(alias: str, ca: dict[str, Any]) -> None:
    """把 MilvusClient 的 `using` 别名挂到 `pymilvus.orm.connections` 上（ORM Collection 依赖）。"""
    if not alias:
        return
    from pymilvus import connections

    if connections.has_connection(alias):
        return
    connections.connect(
        alias,
        uri=str(ca.get("uri", "")),
        token=str(ca.get("token", "") or ""),
        user=str(ca.get("user", "") or ""),
        password=str(ca.get("password", "") or ""),
        db_name="default",
        _unbind_with_db=True,
    )


def prime_orm_connection_before_langchain_milvus() -> None:
    """
    在 **构造** `langchain_milvus.Milvus` **之前** 调用（读接口必需）。

    与 ingest 时「空库先建」不同：若 `week03_hr` 已存在，`Milvus.__init__` 末尾的 `_init`
    → `_extract_fields` 会立刻访问 `self.col`，内部 `Collection(using=alias)` 需要
    `connections` 里已有该 alias。原先只在 `Milvus()` **之后** 补 `connect`，
    会在 **__init__ 未结束** 时失败。

    先 `MilvusClient(**connection_args())` 一次：与随后 LangChain 里新建的 MilvusClient
    在多数情况下**复用同一 ConnectionManager handler**，因而 `_using` 一致，提前
    `connections.connect` 即与后续 `Collection` 对齐。
    """
    from pymilvus import MilvusClient

    ca = connection_args()
    c = MilvusClient(**ca)
    _register_orm_if_missing(c._using, ca)


def register_orm_connection_for_langchain_milvus(store: Any) -> None:
    """
    langchain_milvus 同时用 **MilvusClient** 与 ORM `Collection(using=alias)`。

    在拿到 `Milvus` 实例后补注册（ingest 写路径、或与 prime 成对兜底）。
    """
    ca = connection_args()
    alias = getattr(store, "alias", None) or getattr(store.client, "_using", None)
    _register_orm_if_missing(str(alias) if alias else "", ca)


def ensure_milvus_lite_for_local_db() -> None:
    """
    仅当 `uri` 指向本地 `*.db` 时需要 **milvus-lite** 包；pymilvus 会 `import milvus_lite.server_manager`。

    未安装时，官方报错只有一句 pip 提示，这里把常见原因写全（装错环境 / Python 版本无轮子）。
    """
    uri = str(connection_args().get("uri", "")).strip()
    if not uri.lower().endswith(".db"):
        return
    try:
        from milvus_lite.server_manager import server_manager_instance  # noqa: F401
    except ImportError as e:
        py = f"{sys.version_info.major}.{sys.version_info.minor}"
        raise RuntimeError(
            "当前连接为本地 Milvus Lite 文件（uri 以 .db 结尾），需要已安装 `milvus-lite` 包，"
            "并能在当前解释器里执行：\n"
            "  from milvus_lite.server_manager import server_manager_instance\n\n"
            "请在本机**当前使用的 conda/venv 里**执行：\n"
            "  pip install -U 'pymilvus[milvus_lite]>=2.4.2' 'milvus-lite>=2.4.0' 'setuptools>=69,<81'\n"
            "（`setuptools>=81` 时可能缺少 `pkg_resources`，会导致 milvus-lite 导入失败，见本仓 requirements。）\n"
            "再验证：\n"
            f"  python -c \"from milvus_lite.server_manager import server_manager_instance\"\n\n"
            f"你当前 Python 为 {py}。若 `pip install milvus-lite` 仍失败，多为该版本暂无预编译轮；"
            "可换 Python 3.10～3.12 新建环境，**或**不装 Lite、改用 Docker/远程 Milvus：\n"
            "  export MILVUS_URI=http://127.0.0.1:19530\n"
            f"\n原始 ImportError: {e}"
        ) from e


def connection_summary() -> str:
    """健康检查用摘要，不输出口令。"""
    uri = os.environ.get("MILVUS_URI", "").strip()
    host = os.environ.get("MILVUS_HOST", "").strip()
    if uri:
        if uri.startswith("http") and "@" in uri:
            return "uri=" + uri.split("@", 1)[-1]
        return f"uri={uri}"
    if host:
        p = os.environ.get("MILVUS_PORT", "19530")
        return f"{host}:{p}"
    return f"uri={_DEFAULT_LITE_PATH.name} (milvus-lite)"


def server_and_collection_ok() -> tuple[bool, bool]:
    """
    返回 (能连上 Milvus, 集合 week03_hr 已存在)。

    与 langchain_milvus 相同，使用 MilvusClient(**connection_args()) 探测；仅用于 /health，失败不抛给路由。
    """
    try:
        from pymilvus import MilvusClient

        # `**dict` 把键值对拆成具名入参，等价于 Java 的 `new MilvusClient(uri=…, token=…)` 这种调用方式
        client = MilvusClient(**connection_args())
        has = bool(client.has_collection(COLLECTION_NAME))
        return True, has
    # 宽捕获：健康检查不向上抛，避免 /health 变 500（和 Spring Actuator 里 probe 常吞异常类似）
    except Exception:
        return False, False
