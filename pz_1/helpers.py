import socket
import threading
from contextlib import contextmanager, suppress
from unittest.mock import MagicMock
lazy from collections.abc import Generator

lazy from lab_4.tcp_server import Address, TcpServer

CLIENT_ADDRESS = ("127.0.0.1", 54321)


def connect(payload: bytes | None = None) -> tuple[socket.socket, socket.socket]:
    server_side, client_side = socket.socketpair()
    if payload is not None:
        client_side.sendall(payload)
        client_side.shutdown(socket.SHUT_WR)
    return server_side, client_side


def read_all(client_side: socket.socket) -> str:
    with client_side, client_side.makefile("r", encoding="utf-8") as stream:
        return stream.read()


def fake_listener(*connections: tuple[socket.socket, Address]) -> MagicMock:
    # Accepts the given connections, then raises KeyboardInterrupt as if Ctrl+C was pressed.
    listener = MagicMock()
    listener.__enter__.return_value = listener
    listener.accept.side_effect = [*connections, KeyboardInterrupt]
    return listener


@contextmanager
def running(server: TcpServer) -> Generator[Address]:
    listener = socket.create_server(("127.0.0.1", 0))

    def serve() -> None:
        with suppress(OSError):
            server.serve_forever(listener)

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    try:
        yield listener.getsockname()[:2]
    finally:
        listener.shutdown(socket.SHUT_RDWR)
        listener.close()
        thread.join(timeout=1)


def unused_port() -> int:
    with socket.create_server(("127.0.0.1", 0)) as probe:
        return probe.getsockname()[1]
