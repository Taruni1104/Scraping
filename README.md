# Multi-source web scraping assignment

This project scrapes the two public practice sites [Books to Scrape](https://books.toscrape.com/) and [Quotes to Scrape](https://quotes.toscrape.com/), cleans their different record shapes into one schema, validates records, removes duplicates, and writes a CSV plus a JSON summary.

## Setup

Python 3.10–3.12 is supported.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

Generated files:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

The scraper follows each site's discovered `Next` link rather than hard-coding page counts. It uses one retrying `requests.Session`, waits 0.5 seconds between requests, and allows the second source to run if the first source fails.

## Common schema

`source`, `source_url`, `name_or_title`, `category`, `price`, `rating`, `author`, `tags`, `description`, and `scraped_at`.

Non-applicable values are empty. Book category and description are intentionally left empty because collecting them would require an additional request for every book detail page; no values are guessed.

## Cleaning and validation

Cleaning normalizes whitespace, quote marks, prices, ratings, tags, and URLs. Validation rejects unknown sources, missing names, invalid URLs, negative/non-numeric prices, and ratings outside 1–5. Rejection reasons are included in the JSON report and log.

## Deduplication

Book fingerprints use normalized `source + title`. Quote fingerprints use normalized `source + author + first 50 characters of quote text`. Normalization lowercases text, removes punctuation, and collapses whitespace. The first occurrence is retained and later duplicates are removed.

## Tests

```powershell
python -m pytest
```

Tests run without internet access and cover cleaning, validation, and duplicate detection.

## Limitations

This is an educational batch scraper. It does not persist checkpoints, run concurrently, or crawl book detail pages. The sources are public practice sites; no authentication, CAPTCHA, access-control bypass, or secrets are used.
