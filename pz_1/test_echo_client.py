lazy from collections.abc import Generator

import pytest

from lab_4 import echo_client
from lab_4.echo_server import HOST, PORT, EchoServer
from pz_1.helpers import running, unused_port
lazy from lab_4.tcp_server import Address


@pytest.fixture
def server_address() -> Generator[Address]:
    with running(EchoServer("127.0.0.1", 0)) as address:
        yield address


def test_echo_returns_server_reply(server_address: Address) -> None:
    assert echo_client.echo("Hello, server", *server_address) == "Hello, server"


def test_echo_keeps_unicode_and_long_messages(server_address: Address) -> None:
    message = "Привіт, сервер! " * 500
    assert echo_client.echo(message, *server_address) == message


def test_echo_fails_without_server() -> None:
    with pytest.raises(ConnectionRefusedError):
        echo_client.echo("Hello", "127.0.0.1", unused_port())


def test_parse_args_uses_defaults() -> None:
    args = echo_client.parse_args([])
    assert (args.message, args.host, args.port) == ("Hello, world", HOST, PORT)


def test_parse_args_reads_message_and_address() -> None:
    args = echo_client.parse_args(["Hi", "--host", "10.0.0.5", "--port", "6000"])
    assert (args.message, args.host, args.port) == ("Hi", "10.0.0.5", 6000)


def test_main_prints_sent_and_received(server_address: Address, capsys: pytest.CaptureFixture[str]) -> None:
    host, port = server_address
    echo_client.main(["Hello", "--host", host, "--port", str(port)])
    assert capsys.readouterr().out.endswith("Sent:     Hello\nReceived: Hello\n")


def test_main_exits_when_server_is_down() -> None:
    port = unused_port()
    with pytest.raises(SystemExit, match=f"Echo server is not running on 127.0.0.1:{port}"):
        echo_client.main(["Hello", "--port", str(port)])


def test_main_exits_when_host_is_unknown() -> None:
    with pytest.raises(SystemExit, match="Connection failed"):
        echo_client.main(["Hello", "--host", "no-such-host.invalid"])
