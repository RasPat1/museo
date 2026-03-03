"""CLI entry point — run all museum scrapers.

Usage:
    python -m scraper
"""

from __future__ import annotations

import sys
import time

from .db import init_db, get_connection
from .getty import GettyScraper
from .lacma import LACMAScraper
from .broad import BroadScraper
from .nhm import NHMScraper
from .moca import MOCAScraper


ALL_SCRAPERS = [
    GettyScraper,
    LACMAScraper,
    BroadScraper,
    NHMScraper,
    MOCAScraper,
]


def main() -> None:
    print("═" * 50)
    print("  Museo — Museum Exhibit Scraper")
    print("═" * 50)
    print()

    # Initialise database & seed museums
    init_db()
    print()

    conn = get_connection()
    total = 0

    for scraper_cls in ALL_SCRAPERS:
        name = scraper_cls.museum_id
        print(f"⏳ Scraping {name}...")
        start = time.time()

        try:
            scraper = scraper_cls(conn)
            count = scraper.run()
            elapsed = time.time() - start
            print(f"  ✓ {count} exhibits ({elapsed:.1f}s)")
            total += count
        except Exception as e:
            elapsed = time.time() - start
            print(f"  ✗ Failed ({elapsed:.1f}s): {e}")

    print()
    print(f"Done — {total} exhibits total.")

    # Quick summary
    row = conn.execute("SELECT COUNT(*) as n FROM exhibits").fetchone()
    print(f"Database now has {row['n']} exhibits across all museums.")
    conn.close()


if __name__ == "__main__":
    main()
