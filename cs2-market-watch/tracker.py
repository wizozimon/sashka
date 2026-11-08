"""Track Steam Community Market price snapshots for CS2 items."""
import argparse
import sqlite3
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
import requests

DB = "market.db"
URL = "https://steamcommunity.com/market/priceoverview/"
APP_ID = 730
CURRENCY_ID = 1  # USD


def connect():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS watchlist (item TEXT PRIMARY KEY)")
    con.execute("""CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY, item TEXT NOT NULL, captured_at TEXT NOT NULL,
        lowest_price TEXT, median_price TEXT, volume INTEGER,
        UNIQUE(item, captured_at))""")
    return con


def add(item):
    with connect() as con:
        con.execute("INSERT OR IGNORE INTO watchlist(item) VALUES (?)", (item,))
    print(f"Watching: {item}")


def fetch(item):
    params = {"appid": APP_ID, "currency": CURRENCY_ID, "market_hash_name": item}
    response = requests.get(URL, params=params,
                            headers={"User-Agent": "CS2MarketWatch/1.0 (personal analytics project)"}, timeout=20)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise ValueError("Steam did not return a successful price overview")
    return data


def update():
    with connect() as con:
        items = [row[0] for row in con.execute("SELECT item FROM watchlist ORDER BY item")]
        for i, item in enumerate(items):
            try:
                data = fetch(item)
                con.execute("INSERT OR IGNORE INTO prices(item,captured_at,lowest_price,median_price,volume) VALUES (?,?,?,?,?)",
                            (item, datetime.now(timezone.utc).isoformat(timespec="seconds"),
                             data.get("lowest_price"), data.get("median_price"),
                             int(data["volume"].replace(",", "")) if data.get("volume") else None))
                print(f"{item}: lowest={data.get('lowest_price')} median={data.get('median_price')} volume={data.get('volume', 'n/a')}")
            except (requests.RequestException, ValueError, KeyError) as exc:
                print(f"Skipped {item}: {exc}")
            if i < len(items) - 1:
                time.sleep(3)


def report():
    with connect() as con:
        items = con.execute("SELECT item FROM watchlist ORDER BY item").fetchall()
        for (item,) in items:
            rows = con.execute("SELECT captured_at,lowest_price,median_price,volume FROM prices WHERE item=? ORDER BY captured_at DESC LIMIT 2", (item,)).fetchall()
            print(f"\n{item}")
            for row in rows:
                print("  ", " | ".join(str(x) if x is not None else "n/a" for x in row))
            if len(rows) == 2:
                print(f"  previous-to-latest median: {rows[1][2]} -> {rows[0][2]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_add = sub.add_parser("add"); p_add.add_argument("item")
    sub.add_parser("update"); sub.add_parser("report")
    args = parser.parse_args()
    {"add": lambda: add(args.item), "update": update, "report": report}[args.command]()


if __name__ == "__main__":
    main()
