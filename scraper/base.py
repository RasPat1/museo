"""Base scraper class — all per-museum scrapers inherit from this."""

from __future__ import annotations

import sqlite3
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """Abstract base for museum exhibit scrapers."""

    museum_id: str  # Must be set by subclass

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Museo/1.0 (museum exhibit aggregator; "
                    "contact: museo@example.com)"
                )
            }
        )

    # ── Public API ──────────────────────────────────────────────

    def run(self) -> int:
        """Scrape exhibits and upsert into the database.

        Returns the number of exhibits upserted.
        """
        exhibits = self.scrape()
        now = datetime.now(timezone.utc).isoformat()

        for ex in exhibits:
            self.conn.execute(
                """
                INSERT INTO exhibits (id, museum_id, title, description,
                                      image_url, start_date, end_date, url,
                                      scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title       = excluded.title,
                    description = excluded.description,
                    image_url   = excluded.image_url,
                    start_date  = excluded.start_date,
                    end_date    = excluded.end_date,
                    url         = excluded.url,
                    scraped_at  = excluded.scraped_at
                """,
                (
                    ex["id"],
                    self.museum_id,
                    ex["title"],
                    ex.get("description"),
                    ex.get("image_url"),
                    ex.get("start_date"),
                    ex.get("end_date"),
                    ex.get("url"),
                    now,
                ),
            )

        self.conn.commit()
        return len(exhibits)

    # ── Helpers ─────────────────────────────────────────────────

    def fetch_description(self, url: str, delay: float = 0.3) -> str | None:
        """Fetch an exhibit page and extract the best available description.

        Strategy:
          1. OG description meta tag (most museums have this)
          2. meta[name=description]
          3. First substantial <p> in the main content area

        A small delay is inserted between requests to be polite.
        """
        if not url:
            return None

        time.sleep(delay)

        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "lxml")

            # 1. OG description
            og = soup.find("meta", property="og:description")
            if og and og.get("content", "").strip():
                desc = og["content"].strip()
                if len(desc) > 30:  # skip trivially short ones
                    return desc

            # 2. meta description
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content", "").strip():
                desc = meta["content"].strip()
                if len(desc) > 30:
                    return desc

            # 3. First substantial <p> in the body
            for p in soup.select("main p, article p, .content p, .field p, .body p, p"):
                text = p.get_text(strip=True)
                if len(text) > 60:
                    return text

        except Exception:
            pass

        return None

    # ── Subclass contract ───────────────────────────────────────

    @abstractmethod
    def scrape(self) -> list[dict]:
        """Return a list of exhibit dicts.

        Each dict must contain at minimum:
            id:    str  — unique across the museum (museum_id + slug)
            title: str

        Optional keys: description, image_url, start_date, end_date, url
        """
        ...

