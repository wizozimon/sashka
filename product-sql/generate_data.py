"""Создаём небольшой повторяемый набор событий для SQL-запросов."""
import sqlite3
from datetime import datetime, timedelta, timezone
import numpy as np

DB = "analytics.db"
SEED = 17
N_USERS = 1000


def main():
    rng = np.random.default_rng(SEED)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    con = sqlite3.connect(DB)
    con.execute("DROP TABLE IF EXISTS events")
    con.execute("CREATE TABLE events(user_id INTEGER, event_name TEXT, event_time TEXT)")
    rows = []
    for user in range(1, N_USERS + 1):
        signup_day = int(rng.integers(0, 30))
        signup = start + timedelta(days=signup_day, minutes=int(rng.integers(0, 1440)))
        rows.append((user, "view", (signup - timedelta(minutes=5)).isoformat()))
        rows.append((user, "signup", signup.isoformat()))
        if rng.random() < .28:
            rows.append((user, "purchase", (signup + timedelta(hours=int(rng.integers(1, 72)))).isoformat()))
        if rng.random() < .35:
            back = signup + timedelta(days=int(rng.integers(1, 8)))
            rows.append((user, "view", back.isoformat()))
    con.executemany("INSERT INTO events VALUES (?, ?, ?)", rows)
    con.execute("CREATE INDEX idx_events_user_time ON events(user_id, event_time)")
    con.commit()
    con.close()
    print(f"Created {DB} with {len(rows)} events for {N_USERS} synthetic users.")


if __name__ == "__main__":
    main()
