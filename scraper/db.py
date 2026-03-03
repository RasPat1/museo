"""Database setup and helpers for the Museo scraper."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "exhibits.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS museums (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    city        TEXT NOT NULL DEFAULT 'Los Angeles',
    address     TEXT,
    url         TEXT,
    lat         REAL,
    lng         REAL
);

CREATE TABLE IF NOT EXISTS exhibits (
    id          TEXT PRIMARY KEY,
    museum_id   TEXT NOT NULL REFERENCES museums(id),
    title       TEXT NOT NULL,
    description TEXT,
    image_url   TEXT,
    start_date  TEXT,
    end_date    TEXT,
    url         TEXT,
    scraped_at  TEXT NOT NULL
);
"""

SEED_MUSEUMS = [
    {
        "id": "getty-center",
        "name": "Getty Center",
        "city": "Los Angeles",
        "address": "1200 Getty Center Dr, Los Angeles, CA 90049",
        "url": "https://www.getty.edu/visit/center/",
        "lat": 34.0780,
        "lng": -118.4741,
    },
    {
        "id": "getty-villa",
        "name": "Getty Villa",
        "city": "Los Angeles",
        "address": "17985 Pacific Coast Hwy, Pacific Palisades, CA 90272",
        "url": "https://www.getty.edu/visit/villa/",
        "lat": 34.0459,
        "lng": -118.5650,
    },
    {
        "id": "lacma",
        "name": "Los Angeles County Museum of Art (LACMA)",
        "city": "Los Angeles",
        "address": "5905 Wilshire Blvd, Los Angeles, CA 90036",
        "url": "https://www.lacma.org/",
        "lat": 34.0639,
        "lng": -118.3592,
    },
    {
        "id": "the-broad",
        "name": "The Broad",
        "city": "Los Angeles",
        "address": "221 S Grand Ave, Los Angeles, CA 90012",
        "url": "https://www.thebroad.org/",
        "lat": 34.0544,
        "lng": -118.2508,
    },
    {
        "id": "nhm",
        "name": "Natural History Museum of Los Angeles County",
        "city": "Los Angeles",
        "address": "900 W Exposition Blvd, Los Angeles, CA 90007",
        "url": "https://nhm.org/",
        "lat": 34.0171,
        "lng": -118.2887,
    },
    {
        "id": "moca",
        "name": "Museum of Contemporary Art (MOCA)",
        "city": "Los Angeles",
        "address": "250 S Grand Ave, Los Angeles, CA 90012",
        "url": "https://www.moca.org/",
        "lat": 34.0533,
        "lng": -118.2501,
    },
]


def get_connection() -> sqlite3.Connection:
    """Return a connection to the exhibits database, creating it if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables and seed museum data."""
    conn = get_connection()
    conn.executescript(SCHEMA)

    for m in SEED_MUSEUMS:
        conn.execute(
            """
            INSERT OR IGNORE INTO museums (id, name, city, address, url, lat, lng)
            VALUES (:id, :name, :city, :address, :url, :lat, :lng)
            """,
            m,
        )

    conn.commit()
    conn.close()
    print(f"✓ Database initialised at {DB_PATH}")
