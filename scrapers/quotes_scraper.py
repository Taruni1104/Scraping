"""Scraper for Quotes to Scrape."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class QuotesScraper(BaseScraper):
    """Collect raw quote dictionaries by following the site's next links."""

    start_url = "https://quotes.toscrape.com/"

    def scrape(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        current_url: str | None = self.start_url
        while current_url:
            response = self.fetch(current_url)
            if response is None:
                break
            soup = BeautifulSoup(response.text, "lxml")
            for quote in soup.select("div.quote"):
                try:
                    text_node = quote.select_one("span.text")
                    author_node = quote.select_one("small.author")
                    if text_node is None or author_node is None:
                        raise ValueError("missing quote text or author")
                    author_link = quote.select_one('a[href^="/author/"]')
                    tags = [tag.get_text(" ", strip=True) for tag in quote.select("a.tag")]
                    records.append(
                        {
                            "source": "Quotes to Scrape",
                            "source_url": (
                                urljoin(current_url, author_link["href"])
                                if author_link and author_link.get("href")
                                else current_url
                            ),
                            "name_or_title": text_node.get_text(" ", strip=True),
                            "category": None,
                            "price": None,
                            "rating": None,
                            "author": author_node.get_text(" ", strip=True),
                            "tags": tags,
                            "description": None,
                            "scraped_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                except (AttributeError, TypeError, ValueError) as exc:
                    self.logger.warning("Skipping malformed quote on %s: %s", current_url, exc)
            next_link = soup.select_one("li.next a")
            current_url = urljoin(current_url, next_link["href"]) if next_link and next_link.get("href") else None
        return records
