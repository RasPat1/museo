/**
 * Thin read-only SQLite wrapper for the Museo exhibit database.
 * Used by API routes on the server side.
 *
 * Note: We use process.cwd() to locate the DB because Next.js Turbopack
 * doesn't reliably support import.meta.url for native addons.
 * process.cwd() always resolves to the Next.js project root (web/).
 */

import Database from "better-sqlite3";
import path from "path";

// DB lives at web/data/exhibits.db — bundled with the deployment
const DB_PATH = path.resolve(process.cwd(), "data/exhibits.db");

let _db = null;

function getDb() {
    if (!_db) {
        _db = new Database(DB_PATH, { readonly: true });
    }
    return _db;
}

/** Get all museums. */
export function getMuseums() {
    const db = getDb();
    return db.prepare("SELECT * FROM museums ORDER BY name").all();
}

/** Get exhibits, optionally filtered by museum IDs. */
export function getExhibits({ museumIds = [], search = "" } = {}) {
    const db = getDb();
    let query = `
    SELECT e.*, m.name as museum_name
    FROM exhibits e
    JOIN museums m ON e.museum_id = m.id
  `;
    const conditions = [];
    const params = [];

    if (museumIds.length > 0) {
        const placeholders = museumIds.map(() => "?").join(", ");
        conditions.push(`e.museum_id IN (${placeholders})`);
        params.push(...museumIds);
    }

    if (search) {
        conditions.push("(e.title LIKE ? OR e.description LIKE ?)");
        params.push(`%${search}%`, `%${search}%`);
    }

    if (conditions.length > 0) {
        query += " WHERE " + conditions.join(" AND ");
    }

    query += " ORDER BY e.title";
    return db.prepare(query).all(...params);
}

/** Get a single exhibit by ID. */
export function getExhibitById(id) {
    const db = getDb();
    return db
        .prepare(
            `SELECT e.*, m.name as museum_name, m.address as museum_address
       FROM exhibits e
       JOIN museums m ON e.museum_id = m.id
       WHERE e.id = ?`
        )
        .get(id);
}
