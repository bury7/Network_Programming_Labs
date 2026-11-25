# Tasks for Lab 2

Working with the HTTP protocol: a web server built with a Python web framework.

## Task 1.
Install a Python web framework (for example, Flask or Bottle) and start a web server on port 8000.

## Task 2.
Handle a GET request on the server. Return the string "Hello World!".

## Task 3.
Handle a GET request with a path and URL parameters, for example `http://127.0.0.1:8000/currency?today&key=value`. Return a static exchange rate, for example "USD - 41,5". Read the request parameters with `request.args.get()` in Flask or `request.query()` in Bottle.

## Task 4.
Handle request headers. Depending on the value of the `Content-Type` header (`application/json` or `application/xml`), return a JSON or XML document. If the header is missing, return plain text. Read the headers with `request.headers.get` in Flask or `request.get_header[]` in Bottle.

## Task 5.
Handle a GET request with a path and URL parameters `http://127.0.0.1:8000/currency?<param>`, where `param` is one of:
- `today` — the USD rate for today;
- `yesterday` — the USD rate for the previous day.

Request the exchange rates dynamically from the official NBU website according to the API specification: https://bank.gov.ua/admin_uploads/article/Instr_API_KURS_VAL_data.pdf

## Task 6.
Handle a POST request on the server. The request body contains text data. Save the data on the server:
- to a file;
- to an SQLite3 database.

## References
- Flask tutorial: https://flask.palletsprojects.com/en/stable/quickstart/
- Bottle tutorial: https://bottlepy.org/docs/dev/tutorial.html

## Solutions

All servers use Flask and listen on http://127.0.0.1:8000, so run one at a time.

| Task | File                                     | Endpoint                                            |
|------|------------------------------------------|-----------------------------------------------------|
| 1–2  | [hello.py](hello.py)                     | `GET /` returns "Hello World!"                      |
| 3–4  | [currency_static.py](currency_static.py) | `GET /currency` returns a static rate               |
| 5    | [currency_nbu.py](currency_nbu.py)       | `GET /currency?today` or `?yesterday` asks the NBU  |
| 6    | [messages.py](messages.py)               | `POST /messages` saves text to a file and SQLite    |

## How to run

Run every command from the repository root. Install the dependencies once:

```bash
uv sync
```

Start a server in one terminal and send requests from another (curl or Postman). Stop the server with Ctrl+C.

### Tasks 1–2 — Hello World
```bash
uv run python -m lab_2.hello
curl http://127.0.0.1:8000/
```

### Tasks 3–4 — static rate, query parameters and headers
The `currency` parameter picks the currency (USD by default); other parameters such as `today` are accepted.

```bash
uv run python -m lab_2.currency_static
curl "http://127.0.0.1:8000/currency?today&key=value"
curl "http://127.0.0.1:8000/currency?today&currency=EUR"
```

The response format depends on the `Content-Type` request header:

| `Content-Type`     | Response                                                                   |
|--------------------|----------------------------------------------------------------------------|
| `application/json` | `{"currency": "USD", "rate": 41.5}`                                        |
| `application/xml`  | `<exchange_rate><currency>USD</currency><rate>41.5</rate></exchange_rate>` |
| missing or other   | `USD - 41,5`                                                               |

```bash
curl -H "Content-Type: application/json" "http://127.0.0.1:8000/currency?today"
curl -H "Content-Type: application/xml" "http://127.0.0.1:8000/currency?today"
```

### Task 5 — live NBU rate
Pass exactly one of `today` or `yesterday`. The `Content-Type` header works as in task 4.

```bash
uv run python -m lab_2.currency_nbu
curl "http://127.0.0.1:8000/currency?today"
curl -H "Content-Type: application/json" "http://127.0.0.1:8000/currency?yesterday"
```

### Task 6 — POST and storage
The text is appended to `lab_2/messages.txt` and inserted into the `messages` table of `lab_2/messages.db`. The response contains the ID of the new row; an empty body gets `400 Bad Request`.

```bash
uv run python -m lab_2.messages
curl --data "Hello, server!" http://127.0.0.1:8000/messages
```
