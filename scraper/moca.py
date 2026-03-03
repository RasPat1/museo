"""Scraper for MOCA exhibitions — https://www.moca.org/exhibitions"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from .base import BaseScraper


class MOCAScraper(BaseScraper):
    museum_id = "moca"

    EXHIBITIONS_URL = "https://www.moca.org/exhibitions"

    def scrape(self) -> list[dict]:
        resp = self.session.get(self.EXHIBITIONS_URL, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        exhibits: list[dict] = []

        # MOCA uses links to /exhibition/<slug>
        links = soup.select("a[href*='/exhibition/']")

        seen_slugs: set[str] = set()

        for link in links:
            href = link.get("href", "")
            if "/exhibition/" not in href:
                continue

            slug = href.rstrip("/").split("/")[-1]

            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            exhibit_url = href if href.startswith("http") else f"https://www.moca.org{href}"
            exhibit_id = f"moca-{slug}"

            # Title: look for headings near the link
            title_el = link.select_one("h2, h3, h4, .title")
            if title_el:
                title = title_el.get_text(strip=True)
            else:
                # The link text itself often contains the title
                title = link.get_text(strip=True)
                # Clean up location prefixes
                for prefix in ["MOCA Grand Avenue", "The Geffen Contemporary at MOCA"]:
                    title = title.replace(prefix, "").strip()

            if not title or len(title) > 300:
                continue

            # Image
            img = link.select_one("img")
            image_url = None
            if img:
                image_url = img.get("src") or img.get("data-src")

            exhibits.append(
                {
                    "id": exhibit_id,
                    "title": title,
                    "description": None,
                    "image_url": image_url,
                    "start_date": None,
                    "end_date": None,
                    "url": exhibit_url,
                }
            )

        # Second pass: fetch descriptions from individual exhibit pages
        for i, ex in enumerate(exhibits):
            if not ex.get("description") and ex.get("url"):
                desc = self.fetch_description(ex["url"])
                if desc:
                    exhibits[i]["description"] = desc

        return exhibits
