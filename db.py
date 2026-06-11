"""SQLite storage and dedupe for tenders."""
import sqlite3
from contextlib import contextmanager

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS tenders (
    uid TEXT PRIMARY KEY,          -- source:source_id
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    country TEXT,
    region TEXT,
    notice_type TEXT,
    procurement_method TEXT,
    project_name TEXT,
    reference_no TEXT,
    deadline TEXT,                 -- ISO date string
    url TEXT,
    raw_excerpt TEXT,
    fetched_at TEXT DEFAULT (datetime('now')),
    posted_at TEXT                 -- NULL until posted to Telegram
);
CREATE INDEX IF NOT EXISTS idx_unposted ON tenders(posted_at) WHERE posted_at IS NULL;
"""


@contextmanager
def connect():
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init():
    with connect() as con:
        con.executescript(SCHEMA)


def upsert(tender: dict) -> bool:
    """Insert tender if new. Returns True if it was newly inserted."""
    uid = f"{tender['source']}:{tender['source_id']}"
    with connect() as con:
        cur = con.execute("SELECT 1 FROM tenders WHERE uid = ?", (uid,))
        if cur.fetchone():
            return False
        con.execute(
            """INSERT INTO tenders
               (uid, source, source_id, title, country, region, notice_type,
                procurement_method, project_name, reference_no, deadline, url, raw_excerpt)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                uid, tender["source"], tender["source_id"], tender["title"],
                tender.get("country"), tender.get("region"), tender.get("notice_type"),
                tender.get("procurement_method"), tender.get("project_name"),
                tender.get("reference_no"), tender.get("deadline"),
                tender.get("url"), tender.get("raw_excerpt"),
            ),
        )
        return True


def unposted(limit: int):
    with connect() as con:
        cur = con.execute(
            "SELECT * FROM tenders WHERE posted_at IS NULL ORDER BY fetched_at LIMIT ?",
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]


def mark_posted(uid: str):
    with connect() as con:
        con.execute("UPDATE tenders SET posted_at = datetime('now') WHERE uid = ?", (uid,))


def stats():
    with connect() as con:
        total = con.execute("SELECT COUNT(*) c FROM tenders").fetchone()["c"]
        pending = con.execute(
            "SELECT COUNT(*) c FROM tenders WHERE posted_at IS NULL"
        ).fetchone()["c"]
        return {"total": total, "pending": pending}
