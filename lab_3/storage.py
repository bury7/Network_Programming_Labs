import sqlite3
from typing import Any, TypedDict
lazy from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    color TEXT NOT NULL
);
"""
INSERT_ITEM = "INSERT INTO items (name, price, color) VALUES (:name, :price, :color) RETURNING *"
DUMMY_HASH = generate_password_hash("unused")

type Item = dict[str, Any]


class NewItem(TypedDict):
    name: str
    price: float
    color: str


def connect(database: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


class UserStore:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, username: str, password: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?) "
                "ON CONFLICT (username) DO UPDATE SET password_hash = excluded.password_hash",
                (username, generate_password_hash(password)),
            )

    def verify(self, username: str, password: str) -> bool:
        row = self.connection.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        # Hash for unknown users too, so the response time does not reveal which usernames exist.
        password_matches = check_password_hash(row["password_hash"] if row else DUMMY_HASH, password)
        return row is not None and password_matches


class Catalog:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_items(self) -> list[Item]:
        return [dict(row) for row in self.connection.execute("SELECT * FROM items ORDER BY id")]

    def get_item(self, item_id: int) -> Item | None:
        row = self.connection.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return dict(row) if row else None

    def add_item(self, item: NewItem) -> Item:
        with self.connection:
            return dict(self.connection.execute(INSERT_ITEM, item).fetchone())

    def update_item(self, item_id: int, item: NewItem) -> Item | None:
        with self.connection:
            row = self.connection.execute(
                "UPDATE items SET name = :name, price = :price, color = :color WHERE id = :id RETURNING *",
                {**item, "id": item_id},
            ).fetchone()
        return dict(row) if row else None

    def delete_item(self, item_id: int) -> bool:
        with self.connection:
            return self.connection.execute("DELETE FROM items WHERE id = ?", (item_id,)).rowcount > 0

    def replace_items(self, items: list[NewItem]) -> list[Item]:
        with self.connection:
            self.connection.execute("DELETE FROM items")
            return [dict(self.connection.execute(INSERT_ITEM, item).fetchone()) for item in items]

    def clear(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM items")
