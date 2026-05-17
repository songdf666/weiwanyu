from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .loaders import iter_input_files, load_documents
from .schema import ProcessedDocument, RawDocument
from .text import normalize_text, simple_tokenize


@dataclass
class PreprocessConfig:
    input_globs: list[str]
    encoding: str = "utf-8"
    text_column: str = "text"
    id_column: str | None = None
    period_column: str | None = None
    period_regex: str | None = r"(18|19|20)\d{2}"
    unicode_normalization: str = "NFKC"
    lowercase: bool = False
    strip_urls: bool = True
    collapse_whitespace: bool = True
    min_chars: int = 1
    tokenize: bool = True
    keep_empty_tokens: bool = False

    @classmethod
    def from_json(cls, path: Path) -> "PreprocessConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)


def run_pipeline(input_dir: Path, output_path: Path, config: PreprocessConfig) -> dict[str, int]:
    input_dir = input_dir.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    stats = {"files": 0, "read": 0, "written": 0, "skipped_short": 0}

    with output_path.open("w", encoding="utf-8") as handle:
        for file_path in iter_input_files(input_dir, config.input_globs):
            stats["files"] += 1
            for raw_doc in load_documents(
                file_path,
                input_root=input_dir,
                encoding=config.encoding,
                text_column=config.text_column,
                id_column=config.id_column,
                period_column=config.period_column,
            ):
                stats["read"] += 1
                processed = preprocess_document(raw_doc, config)
                if processed is None:
                    stats["skipped_short"] += 1
                    continue
                handle.write(json.dumps(processed.to_json(), ensure_ascii=False) + "\n")
                stats["written"] += 1

    return stats


def preprocess_document(
    raw_doc: RawDocument,
    config: PreprocessConfig,
) -> ProcessedDocument | None:
    text = normalize_text(
        raw_doc.text,
        unicode_normalization=config.unicode_normalization,
        lowercase=config.lowercase,
        strip_urls=config.strip_urls,
        collapse_whitespace=config.collapse_whitespace,
    )
    if len(text) < config.min_chars:
        return None

    doc_id = raw_doc.doc_id or _fallback_doc_id(raw_doc)
    period = raw_doc.period or _extract_period(raw_doc.source_path, config.period_regex)
    tokens = simple_tokenize(text, keep_empty_tokens=config.keep_empty_tokens) if config.tokenize else None

    return ProcessedDocument(
        doc_id=doc_id,
        source_path=raw_doc.source_path,
        period=period,
        text=text,
        tokens=tokens,
        meta=raw_doc.meta,
    )


def load_config(path: Path) -> PreprocessConfig:
    return PreprocessConfig.from_json(path)


def _fallback_doc_id(raw_doc: RawDocument) -> str:
    suffix = raw_doc.meta.get("line_no")
    if suffix is None:
        return raw_doc.source_path
    return f"{raw_doc.source_path}:{suffix}"


def _extract_period(source_path: str, period_regex: str | None) -> str | None:
    if not period_regex:
        return None
    match = re.search(period_regex, source_path)
    return match.group(0) if match else None


def stats_to_text(stats: dict[str, Any]) -> str:
    return ", ".join(f"{key}={value}" for key, value in stats.items())
