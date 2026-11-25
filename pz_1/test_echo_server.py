lazy import pytest

from lab_4.echo_server import BUFFER_SIZE, EchoServer
from pz_1.helpers import CLIENT_ADDRESS, connect, read_all


def echo_once(payload: bytes) -> str:
    server_side, client_side = connect(payload)
    EchoServer("127.0.0.1", 0).handle_client(server_side, CLIENT_ADDRESS)
    return read_all(client_side)


def test_handle_sends_data_back() -> None:
    assert echo_once(b"Hello, server") == "Hello, server"


def test_handle_sends_back_data_longer_than_buffer() -> None:
    message = "Привіт! " * BUFFER_SIZE
    assert echo_once(message.encode()) == message


def test_handle_accepts_empty_message() -> None:
    assert echo_once(b"") == ""


def test_handle_logs_client_address(capsys: pytest.CaptureFixture[str]) -> None:
    echo_once(b"ping")
    assert capsys.readouterr().out == "Connected by 127.0.0.1:54321\n"
