# Task for Lab 3

REST API design.

Create a web service that stores a product catalog of a shop. Every product must be described by at least 3 parameters, for example: product ID, price, size, weight, color, etc.

Develop the REST API of the web service with any Python framework (Flask, Bottle, etc.). The web service must:
- implement 2 API endpoints:
  - `/items` — operations on all products in the catalog, for example, listing everything the catalog contains;
  - `/items/<id>` — information about a specific product by its `<id>` attribute;
- support HTTP Basic authentication. User credentials (username and password) must be stored:
  - in a dictionary inside the program (easy);
  - in a file (medium);
  - in an SQLite database (hard);
- handle 4 HTTP methods of the REST API:
  - `GET` to read records;
  - `POST` to create records;
  - `PUT` to update a record;
  - `DELETE` to delete records;
  - the `/items/<id>` endpoint does not need to support `POST`;
- receive requests and build responses in JSON;
- store the product catalog:
  - in a dictionary inside the program (easy);
  - in a file (medium);
  - in an SQLite database (hard).

Then:
- test the web service with Postman (easy);
- write a client for the web service with the `requests` library that reads the catalog and adds, updates and deletes products (medium).

## References
- https://pythonbasics.org/flask-rest-api/
- https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
- https://medium.com/@dennisivy/flask-restful-crud-api-c13c7d82c6e5

## Solution

| Part     | File                                                               | What it does                                    |
|----------|--------------------------------------------------------------------|-------------------------------------------------|
| REST API | [app.py](app.py)                                                   | Flask routes, Basic Auth and input validation   |
| Storage  | [storage.py](storage.py)                                           | `Catalog` and `UserStore` classes over SQLite   |
| Postman  | [catalog.postman_collection.json](catalog.postman_collection.json) | Requests and checks for every endpoint          |
| Client   | [client.py](client.py)                                             | Command-line client built on `requests`         |

Every product has an `id`, `name`, `price` and `color`. Both the catalog and the users live in `lab_3/catalog.db`; passwords are stored as hashes.

| Method   | Endpoint      | Action                                 | Success          |
|----------|---------------|----------------------------------------|------------------|
| `GET`    | `/items`      | List all products                      | `200 OK`         |
| `POST`   | `/items`      | Create a product                       | `201 Created`    |
| `PUT`    | `/items`      | Replace the whole catalog with a list  | `200 OK`         |
| `DELETE` | `/items`      | Delete all products                    | `204 No Content` |
| `GET`    | `/items/<id>` | Get a product                          | `200 OK`         |
| `PUT`    | `/items/<id>` | Update a product                       | `200 OK`         |
| `DELETE` | `/items/<id>` | Delete a product                       | `204 No Content` |

`POST` and `PUT` take a product as JSON with all three fields, for example `{"name": "T-shirt", "price": 499.99, "color": "black"}`. Errors come back as JSON, for example `{"error": "Item 42 not found"}`. A request without valid credentials gets `401 Unauthorized`.

## How to run

Run every command from the repository root. Install the dependencies once and create `.env` from the template:

```bash
uv sync
cp .env.example .env
```

1. Create a user. The command asks for the password twice; running it again for the same user changes the password.
   ```bash
   uv run flask --app lab_3.app add-user admin
   ```
2. Start the server on http://127.0.0.1:8000 and leave it running:
   ```bash
   uv run python -m lab_3.app
   ```
3. Try it with curl:
   ```bash
   curl -u admin:password http://127.0.0.1:8000/items
   curl -u admin:password -H "Content-Type: application/json" \
        --data '{"name": "T-shirt", "price": 499.99, "color": "black"}' http://127.0.0.1:8000/items
   ```

### Postman
Import `lab_3/catalog.postman_collection.json`, set the `username` and `password` collection variables to your user and run the collection with the **Collection Runner**. It goes through every endpoint in order and checks status codes and bodies, including validation errors, a deleted item and a request without credentials.

### Client
Put the same user into `.env` as `CATALOG_USERNAME` and `CATALOG_PASSWORD`, then in a second terminal:

```bash
uv run python -m lab_3.client list
uv run python -m lab_3.client add T-shirt 499.99 black
uv run python -m lab_3.client get 1
uv run python -m lab_3.client update 1 T-shirt 399.99 white
uv run python -m lab_3.client delete 1
```
