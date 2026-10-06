"""Validation rules for the common record model."""

from __future__ import annotations

from typing import Any


ALLOWED_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("source") not in ALLOWED_SOURCES:
        errors.append("unknown source")
    if not record.get("name_or_title"):
        errors.append("missing name_or_title")
    source_url = record.get("source_url", "")
    if not isinstance(source_url, str) or not source_url.startswith(("http://", "https://")):
        errors.append("invalid source_url")
    price = record.get("price")
    if price is not None and (not isinstance(price, (int, float)) or price < 0):
        errors.append("invalid price")
    rating = record.get("rating")
    if rating is not None and (not isinstance(rating, int) or not 1 <= rating <= 5):
        errors.append("invalid rating")
    return errors
