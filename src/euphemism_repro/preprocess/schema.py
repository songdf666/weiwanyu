from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RawDocument:
    doc_id: str | None
    source_path: str
    text: str
    period: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedDocument:
    doc_id: str
    source_path: str
    period: str | None
    text: str
    tokens: list[str] | None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "source_path": self.source_path,
            "period": self.period,
            "text": self.text,
            "tokens": self.tokens,
            "meta": self.meta,
        }
