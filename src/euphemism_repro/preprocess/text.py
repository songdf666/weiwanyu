from __future__ import annotations

import re
import unicodedata

URL_RE = re.compile(r"https?://\S+|www\.\S+")
WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(
    text: str,
    *,
    unicode_normalization: str = "NFKC",
    lowercase: bool = False,
    strip_urls: bool = True,
    collapse_whitespace: bool = True,
) -> str:
    if unicode_normalization:
        text = unicodedata.normalize(unicode_normalization, text)
    if strip_urls:
        text = URL_RE.sub(" ", text)
    if lowercase:
        text = text.lower()
    if collapse_whitespace:
        text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def simple_tokenize(text: str, *, keep_empty_tokens: bool = False) -> list[str]:
    tokens = text.split(" ")
    if keep_empty_tokens:
        return tokens
    return [token for token in tokens if token]
