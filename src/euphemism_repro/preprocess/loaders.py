from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterator

from .schema import RawDocument


def iter_input_files(input_dir: Path, globs: list[str]) -> Iterator[Path]:
    seen: set[Path] = set()
    for pattern in globs:
        for path in input_dir.rglob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                yield path


def load_documents(
    path: Path,
    *,
    input_root: Path,
    encoding: str,
    text_column: str,
    id_column: str | None,
    period_column: str | None,
) -> Iterator[RawDocument]:
    suffix = path.suffix.lower()
    rel_path = path.relative_to(input_root).as_posix()

    if suffix == ".txt":
        text = path.read_text(encoding=encoding)
        yield RawDocument(doc_id=None, source_path=rel_path, text=text, meta={"format": "txt"})
        return

    if suffix == ".jsonl":
        with path.open("r", encoding=encoding) as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                yield RawDocument(
                    doc_id=_optional_str(row.get(id_column)) if id_column else None,
                    source_path=rel_path,
                    text=str(row.get(text_column, "")),
                    period=_optional_str(row.get(period_column)) if period_column else None,
                    meta={"format": "jsonl", "line_no": line_no},
                )
        return

    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open("r", encoding=encoding, newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            for line_no, row in enumerate(reader, start=2):
                yield RawDocument(
                    doc_id=_optional_str(row.get(id_column)) if id_column else None,
                    source_path=rel_path,
                    text=str(row.get(text_column, "")),
                    period=_optional_str(row.get(period_column)) if period_column else None,
                    meta={"format": suffix.lstrip("."), "line_no": line_no},
                )
        return

    raise ValueError(f"Unsupported input file type: {path}")


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    value_str = str(value).strip()
    return value_str or None
