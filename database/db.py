import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db",
)

DEMO_NAME = "Demo User"
DEMO_EMAIL = "demo@spendly.com"
DEMO_PASSWORD = "demo123"


def get_db():
    """Return a SQLite connection with dict-like rows and foreign keys enforced."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # SQLite ignores foreign keys unless this is switched on for each connection.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the tables if they do not exist. Safe to run on every start."""
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


# One expense per fixed category, plus one extra Food row. Amounts are REAL.
SAMPLE_EXPENSES = [
    (450.00, "Food", "Groceries"),
    (120.50, "Transport", "Metro card top-up"),
    (899.00, "Bills", "Mobile recharge"),
    (350.00, "Health", "Pharmacy"),
    (250.00, "Entertainment", "Movie tickets"),
    (1200.00, "Shopping", "Winter jacket"),
    (80.00, "Other", "Stationery"),
    (300.00, "Food", "Dinner out"),
]


def seed_db():
    """Insert a demo user and 8 sample expenses, but only if no users exist yet."""
    conn = get_db()
    try:
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (DEMO_NAME, DEMO_EMAIL, generate_password_hash(DEMO_PASSWORD)),
        )
        user_id = cursor.lastrowid

        # Spread the 8 dates across the current month, from day 1 up to today.
        today = date.today()
        rows = []
        for i, (amount, category, description) in enumerate(SAMPLE_EXPENSES, start=1):
            day = max(1, round(today.day * i / len(SAMPLE_EXPENSES)))
            expense_date = date(today.year, today.month, day).isoformat()
            rows.append((user_id, amount, category, expense_date, description))

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email):
    """Return the user row (id, name, email, password_hash) for this email, or None."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()


def create_user(name, email, password):
    """Insert a user with a hashed password and return the new id.

    Raises sqlite3.IntegrityError if the email is already taken.
    """
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()
