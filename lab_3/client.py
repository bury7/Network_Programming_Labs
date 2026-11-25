import argparse
import os
import sys
from typing import TypedDict

import requests
from dotenv import load_dotenv

DEFAULT_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 10


class Item(TypedDict):
    id: int
    name: str
    price: float
    color: str


class CatalogClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)

    def _request(self, method: str, path: str, payload: dict[str, str | float] | None = None) -> requests.Response:
        response = self.session.request(method, f"{self.base_url}{path}", json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response

    def list_items(self) -> list[Item]:
        return self._request("GET", "/items").json()

    def get_item(self, item_id: int) -> Item:
        return self._request("GET", f"/items/{item_id}").json()

    def create_item(self, name: str, price: float, color: str) -> Item:
        return self._request("POST", "/items", {"name": name, "price": price, "color": color}).json()

    def update_item(self, item_id: int, name: str, price: float, color: str) -> Item:
        return self._request("PUT", f"/items/{item_id}", {"name": name, "price": price, "color": color}).json()

    def delete_item(self, item_id: int) -> None:
        self._request("DELETE", f"/items/{item_id}")


def print_items(items: list[Item]) -> None:
    if not items:
        print("Catalog is empty.")
        return
    print(f"{'ID':>4}  {'Name':<24} {'Price':>10}  Color")
    for item in items:
        print(f"{item['id']:>4}  {item['name']:<24} {item['price']:>10.2f}  {item['color']}")


def describe_error(error: requests.HTTPError) -> str:
    response = error.response
    if response is None:
        return str(error)
    try:
        message = response.json()["error"]
    except ValueError, KeyError, TypeError:
        message = response.reason
    return f"Error {response.status_code}: {message}"


def run(client: CatalogClient, args: argparse.Namespace) -> None:
    match args.command:
        case "list":
            print_items(client.list_items())
        case "get":
            print_items([client.get_item(args.id)])
        case "add":
            print_items([client.create_item(args.name, args.price, args.color)])
        case "update":
            print_items([client.update_item(args.id, args.name, args.price, args.color)])
        case "delete":
            client.delete_item(args.id)
            print(f"Item {args.id} deleted.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Client for the product catalog REST API.")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="show all items")

    get = commands.add_parser("get", help="show an item")
    get.add_argument("id", type=int)

    add = commands.add_parser("add", help="create an item")
    add.add_argument("name")
    add.add_argument("price", type=float)
    add.add_argument("color")

    update = commands.add_parser("update", help="update an item")
    update.add_argument("id", type=int)
    update.add_argument("name")
    update.add_argument("price", type=float)
    update.add_argument("color")

    delete = commands.add_parser("delete", help="delete an item")
    delete.add_argument("id", type=int)

    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    username, password = os.getenv("CATALOG_USERNAME"), os.getenv("CATALOG_PASSWORD")
    if not username or not password:
        sys.exit("Set CATALOG_USERNAME and CATALOG_PASSWORD in .env")

    client = CatalogClient(os.getenv("CATALOG_URL", DEFAULT_URL), username, password)
    try:
        run(client, args)
    except requests.HTTPError as error:
        sys.exit(describe_error(error))
    except requests.RequestException as error:
        sys.exit(f"Request failed: {error}")


if __name__ == "__main__":
    main()
