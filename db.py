import sqlite3
from typing import List, Tuple

DB_PATH = "subscriptions.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id TEXT NOT NULL,
        feed_url TEXT NOT NULL
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS last_seen (
        feed_url TEXT PRIMARY KEY,
        last_published TEXT
    )""")
    conn.commit()
    conn.close()

def add_subscription(channel_id: str, feed_url: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO subscriptions (channel_id, feed_url) VALUES (?, ?)", (channel_id, feed_url))
    conn.commit()
    conn.close()

def remove_subscription(channel_id: str, feed_url: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM subscriptions WHERE channel_id=? AND feed_url=?", (channel_id, feed_url))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted

def list_subscriptions_for_channel(channel_id: str) -> List[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT feed_url FROM subscriptions WHERE channel_id=?", (channel_id,))
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows

def get_all_feeds() -> List[Tuple[str, List[str]]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT feed_url FROM subscriptions")
    feeds = [r[0] for r in cur.fetchall()]
    result = []
    for feed in feeds:
        cur.execute("SELECT channel_id FROM subscriptions WHERE feed_url=?", (feed,))
        channels = [r[0] for r in cur.fetchall()]
        result.append((feed, channels))
    conn.close()
    return result

def get_last_published(feed_url: str) -> str | None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT last_published FROM last_seen WHERE feed_url=?", (feed_url,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def set_last_published(feed_url: str, published: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO last_seen(feed_url, last_published) VALUES (?, ?) ON CONFLICT(feed_url) DO UPDATE SET last_published=excluded.last_published", (feed_url, published))
    conn.commit()
    conn.close()

# init DB on import
init_db()