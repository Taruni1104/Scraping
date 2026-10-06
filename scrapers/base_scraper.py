"""Shared HTTP behavior for the practice-site scrapers."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BaseScraper:
    """Provide a resilient, rate-limited HTTP session."""

    def __init__(
        self,
        *,
        pause_seconds: float = 0.5,
        timeout_seconds: float = 20.0,
        logger: logging.Logger | None = None,
    ) -> None:
        self.pause_seconds = pause_seconds
        self.timeout_seconds = timeout_seconds
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "scraping-assignment/1.0 "
                    "(educational use; contact unavailable)"
                )
            }
        )
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.mount("http://", HTTPAdapter(max_retries=retry))

    def fetch(self, url: str) -> requests.Response | None:
        """Fetch one URL, logging failures instead of aborting the pipeline."""
        self.logger.info("Requesting %s", url)
        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except requests.RequestException as exc:
            self.logger.error("Request failed for %s: %s", url, exc)
            return None
        finally:
            time.sleep(self.pause_seconds)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "BaseScraper":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def pages(self, start_url: str) -> Iterator[tuple[str, requests.Response]]:
        """Yield successful responses while following discovered next links."""
        current_url: str | None = start_url
        while current_url:
            response = self.fetch(current_url)
            if response is None:
                return
            yield current_url, response
            current_url = None
