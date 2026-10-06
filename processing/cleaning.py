"""Pure functions for normalizing scraped values."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any
from urllib.parse import urljoin


RATING_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\xa0", " ").split())


def strip_quotes(value: Any) -> str:
    return clean_text(value).strip("\"“”'‘’")


def clean_price(value: Any) -> float | None:
    if value in (None, ""):
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(value: Any) -> int | None:
    if value in (None, ""):
        return None
    text = clean_text(value).lower()
    if text in RATING_WORDS:
        return RATING_WORDS[text]
    try:
        return int(text)
    except ValueError:
        return None


def clean_tags(value: Any) -> str:
    if value in (None, ""):
        return ""
    values: Iterable[Any] = value.split(",") if isinstance(value, str) else value
    return ";".join(sorted({clean_text(item).lower() for item in values if clean_text(item)}))


def normalize_url(value: Any, base_url: str = "") -> str:
    return urljoin(base_url, clean_text(value))


def clean_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(record)
    for field in ("source", "source_url", "name_or_title", "category", "author", "description"):
        cleaned[field] = clean_text(cleaned.get(field))
    cleaned["source_url"] = normalize_url(cleaned["source_url"])
    cleaned["name_or_title"] = strip_quotes(cleaned["name_or_title"])
    cleaned["price"] = clean_price(cleaned.get("price"))
    cleaned["rating"] = clean_rating(cleaned.get("rating"))
    cleaned["tags"] = clean_tags(cleaned.get("tags"))
    return cleaned
