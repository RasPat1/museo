"""Scraper for Getty exhibitions — https://www.getty.edu/museum/exhibitions

The Getty exhibitions page is partially JS-rendered, so we scrape
the server-rendered HTML which contains exhibit links.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from .base import BaseScraper


class GettyScraper(BaseScraper):
    museum_id = "getty-center"

    EXHIBITIONS_URL = "https://www.getty.edu/museum/exhibitions"

    def scrape(self) -> list[dict]:
        resp = self.session.get(self.EXHIBITIONS_URL, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        exhibits: list[dict] = []

        # Getty exhibit links go to /art/exhibitions/<slug> or /art/collection/...
        links = soup.select("a[href*='/art/exhibitions/'], a[href*='/museum/exhibitions/']")

        seen_slugs: set[str] = set()

        for link in links:
            href = link.get("href", "")
            slug = href.rstrip("/").split("/")[-1]

            if slug in seen_slugs or not slug or slug == "exhibitions":
                continue
            seen_slugs.add(slug)

            exhibit_url = href if href.startswith("http") else f"https://www.getty.edu{href}"
            exhibit_id = f"getty-{slug}"

            # Title
            heading = link.select_one("h2, h3, h4, .title")
            if heading:
                title = heading.get_text(strip=True)
            else:
                title = link.get_text(strip=True)

            if not title or len(title) > 300:
                continue

            # Determine if Center or Villa
            museum_id = self.museum_id  # default to center
            text_block = link.get_text(" ", strip=True).lower()
            if "villa" in text_block or "villa" in href.lower():
                museum_id = "getty-villa"

            # Image
            img = link.select_one("img")
            image_url = None
            if img:
                image_url = img.get("src") or img.get("data-src")

            exhibits.append(
                {
                    "id": exhibit_id,
                    "museum_id_override": museum_id,
                    "title": title,
                    "description": None,
                    "image_url": image_url,
                    "start_date": None,
                    "end_date": None,
                    "url": exhibit_url,
                }
            )

        return exhibits

    def run(self) -> int:
        """Override run to handle museum_id_override for Center vs Villa."""
        from datetime import datetime, timezone

        raw_exhibits = self.scrape()
        now = datetime.now(timezone.utc).isoformat()

        for ex in raw_exhibits:
            museum_id = ex.pop("museum_id_override", self.museum_id)

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
                    museum_id,
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
        return len(raw_exhibits)
