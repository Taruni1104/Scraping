from processing.cleaning import clean_price, clean_rating, clean_tags, clean_text
from processing.deduplication import deduplicate
from processing.validation import validate_record


def test_cleaning_values() -> None:
    assert clean_text(" Hello \n World ") == "Hello World"
    assert clean_price("£51.77") == 51.77
    assert clean_rating("Three") == 3
    assert clean_tags([" Fiction ", "science", "fiction"]) == "fiction;science"


def test_validation_returns_reasons() -> None:
    reasons = validate_record({"source": "unknown", "name_or_title": "", "source_url": "bad"})
    assert reasons == ["unknown source", "missing name_or_title", "invalid source_url"]


def test_deduplication_normalizes_titles() -> None:
    records = [
        {"source": "Books to Scrape", "name_or_title": "Example Book Title"},
        {"source": "Books to Scrape", "name_or_title": " example book title "},
    ]
    unique, duplicate_count = deduplicate(records)
    assert len(unique) == 1
    assert duplicate_count == 1
