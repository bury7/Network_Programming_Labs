# Tasks for Lab 4

Using the Socket API for network applications. Create a client and a server with the Python socket API.

## Task 1.
Develop an echo server with the Python socket API that accepts a connection from a client and sends the received data back. Server example: https://docs.python.org/3/library/socket.html#example

## Task 2.
Develop an echo client with the Python socket API that connects to the server, sends string data and receives the response. Client example: https://docs.python.org/3/library/socket.html#example

## Task 3.
Modify the TCP server from task 1 so that it runs continuously and handles requests from many clients one after another. To test the server, run the client from task 2 several times.

## Task 4.
Develop a TCP server with the Python socket API that receives a text file from a client and saves it locally on the server side.

## Task 5.
Develop a TCP client that sends any text file to the server.

## Solutions

| Task | File                             | Address           | What it does                                                     |
|------|----------------------------------|-------------------|------------------------------------------------------------------|
| 1, 3 | [tcp_server.py](tcp_server.py)   |                   | `TcpServer` base class: accept loop, timeouts, Ctrl+C handling   |
| 1, 3 | [echo_server.py](echo_server.py) | `127.0.0.1:50007` | `EchoServer`: echoes data back; serves clients one after another |
| 2    | [echo_client.py](echo_client.py) |                   | Sends a string and prints the reply                              |
| 4    | [file_server.py](file_server.py) | `127.0.0.1:50008` | `FileServer`: saves received text files to `lab_4/received/`     |
| 5    | [file_client.py](file_client.py) |                   | Sends a text file and prints the server reply                    |

Both servers inherit from `TcpServer`, which serves clients one after another, gives each a 30-second timeout and keeps running when a client misbehaves. A subclass only defines how to `handle` one connection.

The file client sends a short header followed by the file content:

```text
<file name>\n
<size in bytes>\n
<content>
```

The server answers with one line, `OK <file name>` or `ERROR <reason>`. It keeps only the base name of the file, so a client cannot write outside `lab_4/received/`. Files must be UTF-8 text and at most 10 MiB.

## How to run

Run every command from the repository root. Install the dependencies once:

```bash
uv sync
```

Each server runs until you stop it with Ctrl+C, so start it in one terminal and run the client in another.

### Tasks 1–3 — echo
```bash
uv run python -m lab_4.echo_server
```

```bash
uv run python -m lab_4.echo_client "Hello, server"
uv run python -m lab_4.echo_client "One more message"
```

### Tasks 4–5 — file transfer
```bash
uv run python -m lab_4.file_server
```

```bash
uv run python -m lab_4.file_client lab_4/README.md
```

Both clients take `--host` and `--port` to reach a server on another address, for example `uv run python -m lab_4.echo_client "Hi" --host 192.168.0.10 --port 50007`.
