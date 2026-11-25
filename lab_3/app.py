import json
from contextlib import closing
from pathlib import Path
lazy import sqlite3

import click
from flask import Flask, abort, g, jsonify, request, url_for
from werkzeug.datastructures import WWWAuthenticate
from werkzeug.exceptions import HTTPException
lazy from flask.typing import ResponseReturnValue

from lab_3.storage import Catalog, NewItem, UserStore, connect

DATABASE = Path(__file__).with_name("catalog.db")
MAX_PRICE = 1_000_000_000

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = connect(DATABASE)
    return g.db


@app.teardown_appcontext
def close_db(_error: BaseException | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.errorhandler(HTTPException)
def handle_http_error(error: HTTPException) -> ResponseReturnValue:
    response = error.get_response()
    response.data = json.dumps({"error": error.description})
    response.content_type = "application/json"
    return response


@app.before_request
def authenticate() -> None:
    auth = request.authorization
    users = UserStore(get_db())
    if auth is None or auth.type != "basic" or not users.verify(auth.username or "", auth.password or ""):
        abort(
            401,
            "Valid username and password are required",
            www_authenticate=WWWAuthenticate("basic", {"realm": "Catalog"}),
        )


def parse_item(data: object) -> NewItem:
    if not isinstance(data, dict):
        abort(400, "Expected a JSON object with name, price and color")
    name, price, color = data.get("name"), data.get("price"), data.get("color")
    if not isinstance(name, str) or not name.strip():
        abort(400, "name must be a non-empty string")
    if isinstance(price, bool) or not isinstance(price, int | float) or not 0 <= price <= MAX_PRICE:
        abort(400, f"price must be a number from 0 to {MAX_PRICE}")
    if not isinstance(color, str) or not color.strip():
        abort(400, "color must be a non-empty string")
    return {"name": name.strip(), "price": float(price), "color": color.strip()}


@app.get("/items")
def list_items() -> ResponseReturnValue:
    return jsonify(Catalog(get_db()).list_items())


@app.post("/items")
def create_item() -> ResponseReturnValue:
    item = Catalog(get_db()).add_item(parse_item(request.get_json(silent=True)))
    return jsonify(item), 201, {"Location": url_for("get_item", item_id=item["id"])}


@app.put("/items")
def replace_items() -> ResponseReturnValue:
    data = request.get_json(silent=True)
    if not isinstance(data, list):
        abort(400, "Expected a JSON array of items")
    return jsonify(Catalog(get_db()).replace_items([parse_item(entry) for entry in data]))


@app.delete("/items")
def delete_items() -> ResponseReturnValue:
    Catalog(get_db()).clear()
    return "", 204


@app.get("/items/<int:item_id>")
def get_item(item_id: int) -> ResponseReturnValue:
    item = Catalog(get_db()).get_item(item_id)
    if item is None:
        abort(404, f"Item {item_id} not found")
    return jsonify(item)


@app.put("/items/<int:item_id>")
def update_item(item_id: int) -> ResponseReturnValue:
    item = Catalog(get_db()).update_item(item_id, parse_item(request.get_json(silent=True)))
    if item is None:
        abort(404, f"Item {item_id} not found")
    return jsonify(item)


@app.delete("/items/<int:item_id>")
def delete_item(item_id: int) -> ResponseReturnValue:
    if not Catalog(get_db()).delete_item(item_id):
        abort(404, f"Item {item_id} not found")
    return "", 204


@app.cli.command("add-user")
@click.argument("username")
@click.password_option()
def add_user(username: str, password: str) -> None:
    """Create a user or change the password of an existing one."""
    with closing(connect(DATABASE)) as connection:
        UserStore(connection).save(username, password)
    click.echo(f"User {username} saved.")


if __name__ == "__main__":
    app.run(port=8000)
