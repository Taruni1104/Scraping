"""Scraper for Books to Scrape."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class BooksScraper(BaseScraper):
    """Collect raw book dictionaries by following the site's next links."""

    start_url = "https://books.toscrape.com/"

    def scrape(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        current_url: str | None = self.start_url
        while current_url:
            response = self.fetch(current_url)
            if response is None:
                break
            soup = BeautifulSoup(response.text, "lxml")
            for card in soup.select("article.product_pod"):
                try:
                    title_link = card.select_one("h3 a")
                    price_node = card.select_one("p.price_color")
                    rating_node = card.select_one("p.star-rating")
                    if title_link is None or price_node is None:
                        raise ValueError("missing required title or price")
                    title = title_link.get("title") or title_link.get_text(" ", strip=True)
                    href = title_link.get("href")
                    if not title or not href:
                        raise ValueError("missing title or product URL")
                    rating_classes = rating_node.get("class", []) if rating_node else []
                    rating_word = next(
                        (value for value in rating_classes if value != "star-rating"),
                        None,
                    )
                    records.append(
                        {
                            "source": "Books to Scrape",
                            "source_url": urljoin(current_url, href),
                            "name_or_title": title,
                            "category": None,
                            "price": price_node.get_text(" ", strip=True),
                            "rating": rating_word,
                            "author": None,
                            "tags": None,
                            "description": None,
                            "scraped_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                except (AttributeError, TypeError, ValueError) as exc:
                    self.logger.warning("Skipping malformed book on %s: %s", current_url, exc)
            next_link = soup.select_one("li.next a")
            current_url = urljoin(current_url, next_link["href"]) if next_link and next_link.get("href") else None
        return records
