"""Run the multi-source scraping and consolidation pipeline."""

from __future__ import annotations

import csv
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from processing.cleaning import clean_record
from processing.deduplication import deduplicate
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
CSV_FIELDS = [
    "source", "source_url", "name_or_title", "category", "price",
    "rating", "author", "tags", "description", "scraped_at",
]


def configure_logging() -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger("scraper")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOG_DIR / "scraper.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    return logger


def write_outputs(records: list[dict[str, Any]], report: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    with (OUTPUT_DIR / "final_dataset.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows({field: record.get(field, "") for field in CSV_FIELDS} for record in records)
    with (OUTPUT_DIR / "summary_report.json").open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def run() -> dict[str, Any]:
    logger = configure_logging()
    started = time.perf_counter()
    start_time = datetime.now(timezone.utc).isoformat()
    raw_by_source: dict[str, list[dict[str, Any]]] = {}
    with BooksScraper(logger=logger) as books:
        raw_by_source["Books to Scrape"] = books.scrape()
    with QuotesScraper(logger=logger) as quotes:
        raw_by_source["Quotes to Scrape"] = quotes.scrape()

    cleaned: list[dict[str, Any]] = []
    rejected_by_reason: Counter[str] = Counter()
    cleaned_by_source: Counter[str] = Counter()
    rejected_record_count = 0
    for source, raw_records in raw_by_source.items():
        for raw_record in raw_records:
            record = clean_record(raw_record)
            problems = validate_record(record)
            if problems:
                rejected_record_count += 1
                for problem in problems:
                    rejected_by_reason[problem] += 1
                logger.warning("Rejected %s record: %s", source, "; ".join(problems))
                continue
            cleaned.append(record)
            cleaned_by_source[source] += 1

    unique, duplicate_count = deduplicate(cleaned)
    end_time = datetime.now(timezone.utc).isoformat()
    report: dict[str, Any] = {
        "started_at": start_time,
        "finished_at": end_time,
        "duration_seconds": round(time.perf_counter() - started, 3),
        "raw_records_by_source": {source: len(records) for source, records in raw_by_source.items()},
        "cleaned_records_by_source": dict(cleaned_by_source),
        "rejected_records": rejected_record_count,
        "rejected_by_reason": dict(rejected_by_reason),
        "duplicates_removed": duplicate_count,
        "final_record_count": len(unique),
    }
    write_outputs(unique, report)
    logger.info("Wrote %d final records", len(unique))
    return report


if __name__ == "__main__":
    run()
