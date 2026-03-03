"""Scraper for LACMA exhibitions — https://www.lacma.org/exhibitions"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from .base import BaseScraper


class LACMAScraper(BaseScraper):
    museum_id = "lacma"

    EXHIBITIONS_URL = "https://www.lacma.org/exhibitions"

    def scrape(self) -> list[dict]:
        exhibits: list[dict] = []
        page = 0

        while True:
            url = self.EXHIBITIONS_URL if page == 0 else f"{self.EXHIBITIONS_URL}?page={page}"
            resp = self.session.get(url, timeout=30)

            if resp.status_code != 200:
                break

            soup = BeautifulSoup(resp.text, "lxml")
            cards = soup.select("a.card--exhibition, article.card--exhibition, .views-row a[href*='/art/exhibition/']")

            if not cards:
                # Try a broader selector — LACMA's markup varies
                cards = soup.select("a[href*='/art/exhibition/']")

            if not cards:
                break

            seen_before = len(exhibits)

            for card in cards:
                href = card.get("href", "")
                if not href or "/art/exhibition/" not in href:
                    continue

                # Build full URL
                exhibit_url = href if href.startswith("http") else f"https://www.lacma.org{href}"

                # Extract slug for ID
                slug = href.rstrip("/").split("/")[-1]
                exhibit_id = f"lacma-{slug}"

                # Title: try heading inside the card, or card text
                title_el = card.select_one("h2, h3, .card__title, .field--name-title")
                title = title_el.get_text(strip=True) if title_el else card.get_text(strip=True)

                if not title or len(title) > 300:
                    continue

                # Avoid duplicates
                if any(e["id"] == exhibit_id for e in exhibits):
                    continue

                # Try to grab image
                img = card.select_one("img")
                image_url = None
                if img:
                    image_url = img.get("src") or img.get("data-src")

                # Try to extract dates from card text
                date_text = card.select_one(".field--name-field-dates, .date-display-range, .card__date")
                start_date = None
                end_date = None
                if date_text:
                    dates = self._parse_date_range(date_text.get_text(strip=True))
                    if dates:
                        start_date, end_date = dates

                exhibits.append(
                    {
                        "id": exhibit_id,
                        "title": title,
                        "description": None,  # Would need per-exhibit page scrape
                        "image_url": image_url,
                        "start_date": start_date,
                        "end_date": end_date,
                        "url": exhibit_url,
                    }
                )

            # If no new exhibits were found, stop paginating
            if len(exhibits) == seen_before:
                break

            page += 1

        # Second pass: fetch descriptions from individual exhibit pages
        for i, ex in enumerate(exhibits):
            if not ex.get("description") and ex.get("url"):
                desc = self.fetch_description(ex["url"])
                if desc:
                    exhibits[i]["description"] = desc

        return exhibits

    @staticmethod
    def _parse_date_range(text: str) -> tuple[str, str] | None:
        """Try to extract ISO dates from a string like 'March 2, 2025–June 1, 2025'."""
        from datetime import datetime

        # Pattern: Month Day, Year
        pattern = r"([A-Z][a-z]+ \d{1,2},? \d{4})"
        matches = re.findall(pattern, text)
        if len(matches) >= 2:
            try:
                fmt = "%B %d, %Y"
                start = datetime.strptime(matches[0].replace(",", ", ").replace("  ", " ").strip(), fmt)
                end = datetime.strptime(matches[1].replace(",", ", ").replace("  ", " ").strip(), fmt)
                return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return None
