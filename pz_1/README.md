# Task for Pz 1

Unit testing of programs with the `pytest` and `pytest-cov` libraries.

Install the dependencies for writing unit tests:

```bash
pip install pytest pytest-cov
```

Using one of the OOP practical tasks, write unit tests that meet the following requirements:
- the file with unit tests must be named `test_<program name>.py`;
- the program under test must have at least 3 functions or methods;
- every function or method must have at least 2 tests;
- test coverage must be at least 85%. Check the coverage with `pytest --cov=<program name>`;
- generate an HTML coverage report with `pytest --cov=<program name> --cov-report html`.

Upload the program and its tests to a personal GitHub repository.

## Solution

The program under test is the socket client and server package from [Lab 4](../lab_4). Every module has its own `test_<module>.py`. The tests talk to the code over real sockets: `socket.socketpair` for a single connection, and a server running in a background thread for the clients. Uploads go to a temporary directory.

| Module                              | Test file                                  | Tests | What is checked                                                                                                          |
|-------------------------------------|--------------------------------------------|-------|--------------------------------------------------------------------------------------------------------------------------|
| `tcp_server` (`TcpServer`)          | [test_tcp_server.py](test_tcp_server.py)   | 10    | Abstract base, settings, timeouts, closing connections, serving in order, surviving errors, Ctrl+C                       |
| `echo_server` (`EchoServer.handle`) | [test_echo_server.py](test_echo_server.py) | 4     | Echoes text, messages longer than the buffer, empty messages, log line                                                   |
| `echo_client`                       | [test_echo_client.py](test_echo_client.py) | 8     | `echo` reply and refused connection, `parse_args` defaults and options, `main` output and errors                         |
| `file_server` (`FileServer`)        | [test_file_server.py](test_file_server.py) | 23    | `is_text`, settings, saved files, path stripping, invalid names and sizes, truncated and binary files, replies, `run`    |
| `file_client`                       | [test_file_client.py](test_file_client.py) | 11    | `send_file` upload and error reply, `parse_args`, `main` for success, rejected, missing, too large and unreachable cases |

Shared socket helpers live in [helpers.py](helpers.py). Every function and method has at least two tests, all 56 tests pass, and coverage of the whole `lab_4` package is 100% (lines and branches). The run fails if coverage drops below 85%.

## How to run

Run every command from the repository root. Install the dependencies once:

```bash
uv sync
```

Run the tests with a coverage summary:

```bash
uv run pytest --cov=lab_4
```

Build the HTML report and open `htmlcov/index.html` in a browser:

```bash
uv run pytest --cov=lab_4 --cov-report html
```
