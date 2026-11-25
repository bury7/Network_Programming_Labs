import socket
from unittest.mock import Mock

import pytest

from lab_4.tcp_server import CLIENT_TIMEOUT, Address, TcpServer
from pz_1.helpers import CLIENT_ADDRESS, connect, fake_listener, read_all


class GreetingServer(TcpServer):
    name = "Greeting server"

    def __init__(self, host: str = "127.0.0.1", port: int = 0, timeout: float = CLIENT_TIMEOUT) -> None:
        super().__init__(host, port, timeout)
        self.timeouts: list[float | None] = []

    def handle(self, connection: socket.socket, address: Address) -> None:
        self.timeouts.append(connection.gettimeout())
        if connection.recv(1) == b"!":
            raise ConnectionResetError
        connection.sendall(f"hello {address[0]}".encode())


def test_abstract_server_cannot_be_created() -> None:
    with pytest.raises(TypeError, match="abstract"):
        TcpServer("127.0.0.1", 0)  # ty: ignore[abstract-class-instantiation]


def test_init_stores_address_and_timeout() -> None:
    server = GreetingServer("192.168.0.10", 9000, timeout=1.5)
    assert (server.host, server.port, server.timeout) == ("192.168.0.10", 9000, 1.5)


def test_init_uses_default_timeout() -> None:
    assert GreetingServer().timeout == CLIENT_TIMEOUT


def test_handle_client_sets_timeout_and_closes_connection() -> None:
    server = GreetingServer(timeout=2)
    server_side, client_side = connect(b"x")
    server.handle_client(server_side, CLIENT_ADDRESS)
    assert server.timeouts == [2]
    assert server_side.fileno() == -1
    assert read_all(client_side) == "hello 127.0.0.1"


def test_handle_client_closes_connection_on_error() -> None:
    server_side, client_side = connect(b"!")
    with client_side, pytest.raises(ConnectionResetError):
        GreetingServer().handle_client(server_side, CLIENT_ADDRESS)
    assert server_side.fileno() == -1


def test_serve_forever_handles_clients_one_after_another() -> None:
    first_server, first_client = connect(b"a")
    second_server, second_client = connect(b"b")
    with pytest.raises(KeyboardInterrupt):
        GreetingServer().serve_forever(fake_listener((first_server, CLIENT_ADDRESS), (second_server, ("10.0.0.2", 1))))
    assert read_all(first_client) == "hello 127.0.0.1"
    assert read_all(second_client) == "hello 10.0.0.2"


def test_serve_forever_logs_errors_and_keeps_serving(capsys: pytest.CaptureFixture[str]) -> None:
    broken_server, broken_client = connect(b"!")
    good_server, good_client = connect(b"a")
    with broken_client, pytest.raises(KeyboardInterrupt):
        GreetingServer().serve_forever(fake_listener((broken_server, CLIENT_ADDRESS), (good_server, CLIENT_ADDRESS)))
    assert capsys.readouterr().out == "127.0.0.1:54321 connection error: \n"
    assert read_all(good_client) == "hello 127.0.0.1"


def test_serve_forever_drops_idle_clients() -> None:
    server = GreetingServer(timeout=0.05)
    idle_server, idle_client = connect()
    good_server, good_client = connect(b"a")
    with pytest.raises(KeyboardInterrupt):
        server.serve_forever(fake_listener((idle_server, CLIENT_ADDRESS), (good_server, CLIENT_ADDRESS)))
    assert read_all(idle_client) == ""
    assert read_all(good_client) == "hello 127.0.0.1"


def test_run_listens_on_configured_address(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    create_server = Mock(return_value=fake_listener())
    monkeypatch.setattr(socket, "create_server", create_server)

    GreetingServer("127.0.0.1", 8123).run()

    create_server.assert_called_once_with(("127.0.0.1", 8123))
    assert capsys.readouterr().out == (
        "Greeting server is listening on 127.0.0.1:8123, press Ctrl+C to stop\n\nServer stopped\n"
    )


def test_run_serves_clients_until_ctrl_c(monkeypatch: pytest.MonkeyPatch) -> None:
    server_side, client_side = connect(b"a")
    monkeypatch.setattr(socket, "create_server", Mock(return_value=fake_listener((server_side, CLIENT_ADDRESS))))
    GreetingServer().run()
    assert read_all(client_side) == "hello 127.0.0.1"
