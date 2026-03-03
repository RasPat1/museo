"""Scraper for NHM exhibitions — https://nhm.org/exhibitions"""

from __future__ import annotations

from bs4 import BeautifulSoup

from .base import BaseScraper


class NHMScraper(BaseScraper):
    museum_id = "nhm"

    EXHIBITIONS_URL = "https://nhm.org/exhibitions"

    def scrape(self) -> list[dict]:
        resp = self.session.get(self.EXHIBITIONS_URL, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        exhibits: list[dict] = []

        # NHM groups exhibits under sections: Special Exhibitions, Always on View, etc.
        # We'll grab all exhibition links
        links = soup.select("a[href]")

        seen_slugs: set[str] = set()

        for link in links:
            href = link.get("href", "")

            # NHM exhibit URLs look like /exhibitions/dinosaur-hall, /la-underwater, etc.
            # Filter to links that contain exhibition-related content
            # The cards on NHM contain images + titles for exhibits
            img = link.select_one("img")
            heading = link.select_one("h2, h3, h4")

            # We want links that have both an image and some text (exhibit cards)
            if not img and not heading:
                continue

            # Skip navigation/footer links
            if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue

            # Build full URL
            if href.startswith("/"):
                full_url = f"https://nhm.org{href}"
            elif href.startswith("http"):
                full_url = href
                if "nhm.org" not in href:
                    continue
            else:
                continue

            slug = href.rstrip("/").split("/")[-1]
            if slug in seen_slugs or not slug:
                continue
            seen_slugs.add(slug)

            exhibit_id = f"nhm-{slug}"

            # Title
            if heading:
                title = heading.get_text(strip=True)
            else:
                alt = img.get("alt", "") if img else ""
                # Try the link text
                title = link.get_text(strip=True) or alt

            # Clean up — remove "Special Exhibition" prefixes
            for prefix in ["Special Exhibition", "Permanent Exhibition"]:
                title = title.replace(prefix, "").strip()

            if not title or len(title) > 300:
                continue

            # Image URL
            image_url = None
            if img:
                image_url = img.get("src") or img.get("data-src")
                if image_url and image_url.startswith("/"):
                    image_url = f"https://nhm.org{image_url}"

            exhibits.append(
                {
                    "id": exhibit_id,
                    "title": title,
                    "description": None,
                    "image_url": image_url,
                    "start_date": None,
                    "end_date": None,
                    "url": full_url,
                }
            )

        # Second pass: fetch descriptions from individual exhibit pages
        for i, ex in enumerate(exhibits):
            if not ex.get("description") and ex.get("url"):
                desc = self.fetch_description(ex["url"])
                if desc:
                    exhibits[i]["description"] = desc

        return exhibits
