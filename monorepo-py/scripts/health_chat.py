#!/usr/bin/env python3
# 第一行「shebang」：在 Linux/macOS 上可直接 ./health_chat.py 执行（需 chmod +x）。
# Windows 上一般仍用: python scripts/health_chat.py

"""
多行说明（用一对三个英文双引号包裹，中间不要出现连续三个双引号，否则会提前结束，引发语法错误）。

第 0 周 / 第 1 天：最小「健康检查」同步对话（发一句「你好」，打印回复前 200 字）。

在终端中（在 monorepo-py 目录下）：

  cd monorepo-py
  conda activate aimodel
  pip install -r requirements.txt
  cp .env.example .env   # 用编辑器填入密钥
  python scripts/health_chat.py
"""
# ---------------------------------------------------------------------------
# from __future__ import annotations
# 让类型注解里的类型名（如 int、list[str]）在「老版本行为」上更统一；
# 可写可不写，对新手可以忽略，不影响运行。
# ---------------------------------------------------------------------------
from __future__ import annotations

# 标准库：发 HTTP 时常常不用自己拼，本脚本只用到这些
# os  — 读环境变量、访问操作系统相关接口
# sys  — 标准错误输出 sys.stderr、退出码等
import os
import sys

# pathlib.Path：用「面向对象」方式拼路径，比字符串更好维护
# 例如: Path("a") / "b"  在 Windows 上也会自动用正确分隔符
from pathlib import Path


# ===========================================================================
# 模块级「常量」：名字全大写是约定，表示「整份脚本里不应被改掉」的引用
# __file__  是当前这个 .py 文件的路径（由解释器自动注入的魔法变量）
# .resolve()  变成绝对路径，避免受「当前工作目录」影响
# .parent     上级目录 一次  → 得到 scripts/
# 再 .parent 一次           → 得到 monorepo-py/（本 Python 子工程根目录）
# ===========================================================================
_PY_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    """
    以「_」开头：约定表示「本模块内部用」，不建议外部 from xxx import _load_dotenv。

    作用：如果装了 python-dotenv，就从 monorepo-py/.env 里加载 KEY=VALUE
    到环境变量，这样你不必每次手动 export（未安装时静默跳过，不报错）。

    重要：只读「.env」，不要读「.env.example」——
    - .env.example 是仓库里的**模板**（无真密钥、可提交 Git），用 cp 复制成 .env 后自己填 key；
    - .env 才是本地**真密钥**文件（.gitignore 忽略）。load_dotenv 加载的就是这个。
    """
    try:
        # 延迟 import：只有走到这里才尝试加载，避免没装 dotenv 时一启动就失败
        from dotenv import load_dotenv

        # /  对 Path 表示「子路径」
        # 必须是 .env；若本机还没创建，load_dotenv 不报错，只是啥也没读进去（此时靠 export 或先 cp .env.example .env）
        env_file = _PY_ROOT / ".env"
        load_dotenv(env_file)
    except ImportError:
        # 没装 python-dotenv 时：不视为错误，用系统里已 export 的环境变量即可
        # pass 在 Python 里表示「这里故意什么都不做」
        pass


def main() -> int:
    """
    把主要逻辑放 main() 里，是常见习惯，便于测试时「import 本文件不自动跑网请求」。

    返回值是 int，在进程里当「退出码」用：0 表示成功，非 0 表示失败（与 Linux 习惯一致）。
    """
    # 先尝试从 .env 注入环境变量（有则读，无则依赖你在 shell 里 export 的）
    _load_dotenv()

    # -----------------------------------------------------------------------
    # openai 包里的 OpenAI 类：封装了与「OpenAI 风格」兼容的 HTTP 调用
    # （通义、许多国产云也可以用 compatible-mode 的 base_url）
    # -----------------------------------------------------------------------
    try:
        from openai import OpenAI
    except ImportError:
        # print(..., file=sys.stderr)  把字打到「错误流」方便和正常输出分开
        print("请先安装: pip install openai", file=sys.stderr)
        return 1  # 非 0 退出码 = 告诉终端「失败了」

    # os.environ 像字典一样存了所有环境变量；.get("KEY") 若不存在返回 None，不会抛异常
    # 「A or B」：若 A 为假值（None、空串、0 等）则用 B，常用来设「回退项」
    api_key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "未找到密钥：请设置环境变量 DASHSCOPE_API_KEY（通义）或 OPENAI_API_KEY。",
            file=sys.stderr,
        )
        return 1

    # 用户若显式设置了 OPENAI_BASE_URL，优先用；否则按「通义 / OpenAI」给默认
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not base_url and os.environ.get("DASHSCOPE_API_KEY"):
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if not base_url:
        base_url = "https://api.openai.com/v1"

    # 三元表达式：  为真时的值  if 条件  else  为假时的值
    # 行太长可以用括号包起来，或拆行（PEP8 风格）
    model = os.environ.get(
        "LLM_MODEL",
        "qwen-turbo" if os.environ.get("DASHSCOPE_API_KEY") else "gpt-4o-mini",
    )

    # 构造客户端；之后所有「聊天」都通过这个对象发
    client = OpenAI(api_key=api_key, base_url=base_url)

    # -----------------------------------------------------------------------
    # 同步发一条 chat：网络错误、鉴权错都会进 except
    # -----------------------------------------------------------------------
    try:
        resp = client.chat.completions.create(
            model=model,
            # messages 是一条「对话」列表，每条是 role + content
            # 这里只发用户一句；若要多轮，可继续往列表里加 {"role": "assistant", ...}
            messages=[{"role": "user", "content": "你好"}],
            temperature=0.2,  # 越小越稳、越大越发散；健康检查可略低
        )
    # except Exception 会接住几乎所有异常；演示脚本用「打印原因」帮排查即可
    except Exception as e:  # noqa: BLE001 — 本教学脚本略宽捕获，生产代码要细分
        # f-string：在字符串前加 f，大括号 {e} 里会代入变量/表达式
        print(f"请求失败: {e}", file=sys.stderr)
        return 1

    # resp 是库返回的对象，用「点」一层层取：choices[0] 是第一条回复
    # message.content 可能是 None，用  or ""  变成空字符串，再 .strip() 去首尾空白
    text = (resp.choices[0].message.content or "").strip()
    if not text:
        print("（模型返回空内容）", file=sys.stderr)
        return 1

    # 字符串切片：text[:200] 取前 200 个字符（中文通常「字」也占一字符，视编码而定）
    print(text[:200])
    if len(text) > 200:
        # 提醒 stderr：后面还有，避免误以为截断是模型问题
        print("...", file=sys.stderr)
    return 0


# ===========================================================================
# 只有「直接运行本文件」时才会进下面这行；被别的 import 时不会跑 main()
# 这样别人可以: import health_chat  而不触发网络请求
# SystemExit(整数) 会带着退出码结束进程
# ===========================================================================
if __name__ == "__main__":
    raise SystemExit(main())
