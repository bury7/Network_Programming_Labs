import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, abort, request
lazy from flask.typing import ResponseReturnValue

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS messages ("
    "id INTEGER PRIMARY KEY, "
    "text TEXT NOT NULL, "
    "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
)


class MessageStore:
    def __init__(self, text_file: Path, database: Path) -> None:
        self.text_file = text_file
        self.database = database
        with closing(sqlite3.connect(database)) as connection, connection:
            connection.execute(SCHEMA)

    def save(self, text: str) -> int:
        with closing(sqlite3.connect(self.database)) as connection, connection:
            (message_id,) = connection.execute(
                "INSERT INTO messages (text) VALUES (?) RETURNING id", (text,)
            ).fetchone()
        with self.text_file.open("a", encoding="utf-8") as file:
            file.write(f"{text}\n")
        return message_id


store = MessageStore(Path(__file__).with_name("messages.txt"), Path(__file__).with_name("messages.db"))
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024


@app.post("/messages")
def create_message() -> ResponseReturnValue:
    text = request.get_data(as_text=True).strip()
    if not text:
        abort(400, "Message text is empty")
    return {"id": store.save(text), "text": text}, 201


if __name__ == "__main__":
    app.run(port=8000)
