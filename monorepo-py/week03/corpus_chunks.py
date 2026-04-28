"""
与 `week03.ingest` 共用的语料分块逻辑：保证 chunk id（`chunk-0`…）与 Milvus 里一致，供第 5 周 BM25 / 混合检索与评测用。
"""
from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

_ROOT = Path(__file__).resolve().parent.parent
_CORPUS = _ROOT / "data" / "corpus.txt"

_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    length_function=len,
)


def corpus_path() -> Path:
    return _CORPUS


def build_corpus_documents() -> list[Document]:
    """与 `ingest` 中 former `_build_docs` 行为一致，不含 metadata.id（入库时再写）。"""
    if not _CORPUS.is_file():
        return []
    text = _CORPUS.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    docs: list[Document] = []
    for i, line in enumerate(lines):
        if len(line) > 300:
            for j, chunk in enumerate(_SPLITTER.split_text(line)):
                docs.append(Document(page_content=chunk, metadata={"line": i, "sub": j}))
        else:
            docs.append(Document(page_content=line, metadata={"line": i}))
    return docs


def list_chunk_id_text() -> list[tuple[str, str]]:
    """`(chunk-0, text), ...` 与 Milvus 主键一致。"""
    docs = build_corpus_documents()
    return [(f"chunk-{i}", d.page_content or "") for i, d in enumerate(docs)]
