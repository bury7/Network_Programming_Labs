import socket
from unittest.mock import Mock
lazy from pathlib import Path

import pytest

from lab_4.file_server import MAX_FILE_SIZE, FileServer, is_text
from lab_4.tcp_server import CLIENT_TIMEOUT
from pz_1.helpers import CLIENT_ADDRESS, connect, fake_listener, read_all


@pytest.fixture
def upload_dir(tmp_path: Path) -> Path:
    return tmp_path / "received"


@pytest.fixture
def server(upload_dir: Path) -> FileServer:
    return FileServer("127.0.0.1", 0, upload_dir)


def upload_request(name: str, data: bytes) -> bytes:
    return f"{name}\n{len(data)}\n".encode() + data


def receive(server: FileServer, payload: bytes) -> str:
    server_side, client_side = connect(payload)
    with server_side, client_side:
        return server.receive_file(server_side)


def test_is_text_accepts_utf8() -> None:
    assert is_text("Hello, café ✓\n".encode())


def test_is_text_accepts_empty_data() -> None:
    assert is_text(b"")


def test_is_text_rejects_binary_data() -> None:
    assert not is_text(b"\xff\xfe\x00\x01")


def test_init_stores_upload_dir(upload_dir: Path) -> None:
    server = FileServer("127.0.0.1", 9000, upload_dir, timeout=5)
    assert (server.host, server.port, server.upload_dir, server.timeout) == ("127.0.0.1", 9000, upload_dir, 5)


def test_init_uses_default_timeout(server: FileServer) -> None:
    assert server.timeout == CLIENT_TIMEOUT


def test_receive_file_saves_content(server: FileServer, upload_dir: Path) -> None:
    content = "first line\ncafé ✓\n".encode()
    assert receive(server, upload_request("notes.txt", content)) == "OK notes.txt"
    assert (upload_dir / "notes.txt").read_bytes() == content


def test_receive_file_saves_empty_file(server: FileServer, upload_dir: Path) -> None:
    assert receive(server, upload_request("empty.txt", b"")) == "OK empty.txt"
    assert (upload_dir / "empty.txt").read_bytes() == b""


def test_receive_file_overwrites_file_with_same_name(server: FileServer, upload_dir: Path) -> None:
    receive(server, upload_request("notes.txt", b"old"))
    receive(server, upload_request("notes.txt", b"new"))
    assert (upload_dir / "notes.txt").read_bytes() == b"new"


def test_receive_file_keeps_only_base_name(server: FileServer, upload_dir: Path, tmp_path: Path) -> None:
    assert receive(server, upload_request("../../escape.txt", b"data")) == "OK escape.txt"
    assert (upload_dir / "escape.txt").exists()
    assert not (tmp_path / "escape.txt").exists()


@pytest.mark.parametrize("name", ["", ".", "..", "bad\0name.txt"])
def test_receive_file_rejects_invalid_name(server: FileServer, upload_dir: Path, name: str) -> None:
    assert receive(server, upload_request(name, b"data")) == "ERROR invalid file name"
    assert not upload_dir.exists()


@pytest.mark.parametrize("size", [b"abc", b"-1", b"", str(MAX_FILE_SIZE + 1).encode()])
def test_receive_file_rejects_invalid_size(server: FileServer, size: bytes) -> None:
    reply = receive(server, b"notes.txt\n" + size + b"\n")
    assert reply == f"ERROR file size must be a number of bytes up to {MAX_FILE_SIZE}"


def test_receive_file_rejects_truncated_file(server: FileServer, upload_dir: Path) -> None:
    assert receive(server, b"notes.txt\n10\nshort") == "ERROR connection closed before the whole file was received"
    assert not upload_dir.exists()


def test_receive_file_rejects_binary_file(server: FileServer, upload_dir: Path) -> None:
    assert receive(server, upload_request("image.png", b"\x89PNG\xff\xfe")) == "ERROR file is not UTF-8 text"
    assert not upload_dir.exists()


def test_handle_replies_ok_and_logs(server: FileServer, capsys: pytest.CaptureFixture[str]) -> None:
    server_side, client_side = connect(upload_request("notes.txt", b"hello"))
    server.handle_client(server_side, CLIENT_ADDRESS)
    assert read_all(client_side) == "OK notes.txt\n"
    assert capsys.readouterr().out == "127.0.0.1:54321 OK notes.txt\n"


def test_handle_replies_error(server: FileServer) -> None:
    server_side, client_side = connect(upload_request("image.png", b"\xff"))
    server.handle_client(server_side, CLIENT_ADDRESS)
    assert read_all(client_side) == "ERROR file is not UTF-8 text\n"


def test_run_prints_upload_dir_and_stops_on_ctrl_c(
    server: FileServer, upload_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(socket, "create_server", Mock(return_value=fake_listener()))
    server.run()
    output = capsys.readouterr().out
    assert output.startswith(f"Files are saved to {upload_dir}\nFile server is listening on 127.0.0.1:0")
    assert output.endswith("Server stopped\n")


def test_run_saves_upload_before_stopping(
    server: FileServer, upload_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    server_side, client_side = connect(upload_request("report.txt", b"done"))
    monkeypatch.setattr(socket, "create_server", Mock(return_value=fake_listener((server_side, CLIENT_ADDRESS))))
    server.run()
    assert read_all(client_side) == "OK report.txt\n"
    assert (upload_dir / "report.txt").read_bytes() == b"done"
