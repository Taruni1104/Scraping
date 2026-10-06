"""Deterministic duplicate detection."""

from __future__ import annotations

import hashlib
import re
from typing import Any


def _normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", str(value or "").lower())).strip()


def fingerprint(record: dict[str, Any]) -> str:
    if record.get("source") == "Quotes to Scrape":
        key = "|".join(
            (
                _normalize(record.get("source")),
                _normalize(record.get("author")),
                _normalize(record.get("name_or_title"))[:50],
            )
        )
    else:
        key = "|".join((_normalize(record.get("source")), _normalize(record.get("name_or_title"))))
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def deduplicate(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    duplicates = 0
    for record in records:
        key = fingerprint(record)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        unique.append(record)
    return unique, duplicates
