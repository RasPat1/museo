"""Scraper for The Broad exhibitions — https://www.thebroad.org

The Broad's site is a JavaScript SPA that doesn't serve exhibition data
in the initial HTML. For V1 we use a known-exhibitions approach:
we fetch each known exhibit page directly and extract metadata.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from .base import BaseScraper


class BroadScraper(BaseScraper):
    museum_id = "the-broad"

    # The Broad doesn't have a scrapeable index page, so we seed known exhibit
    # page URLs. In a future version this could be replaced with a headless
    # browser or an API if one becomes available.
    KNOWN_EXHIBIT_URLS = [
        "https://www.thebroad.org/art/exhibitions",
        "https://www.thebroad.org/exhibitions",
    ]

    BASE_URL = "https://www.thebroad.org"

    def scrape(self) -> list[dict]:
        exhibits: list[dict] = []

        # Attempt to find exhibit links from possible index pages
        for index_url in self.KNOWN_EXHIBIT_URLS:
            try:
                resp = self.session.get(index_url, timeout=30)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                links = soup.select("a[href*='/exhibition']")

                for link in links:
                    href = link.get("href", "")
                    if not href:
                        continue

                    slug = href.rstrip("/").split("/")[-1]
                    if not slug or slug in ("exhibitions", "exhibition"):
                        continue

                    exhibit_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    exhibit_id = f"broad-{slug}"

                    if any(e["id"] == exhibit_id for e in exhibits):
                        continue

                    heading = link.select_one("h2, h3, h4")
                    title = heading.get_text(strip=True) if heading else link.get_text(strip=True)

                    if not title or len(title) > 300:
                        continue

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

                if exhibits:
                    break  # Found exhibits, no need to try other index URLs

            except Exception:
                continue

        if not exhibits:
            print("  ⚠ The Broad: site is JS-rendered, no exhibits scraped via HTML.")
            print("    Consider adding exhibits manually or using a headless browser.")

        return exhibits
