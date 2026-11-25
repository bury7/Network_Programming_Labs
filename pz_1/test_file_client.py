from pathlib import Path
from unittest.mock import Mock
lazy from collections.abc import Generator

import pytest

from lab_4 import file_client
from lab_4.file_server import HOST, PORT, FileServer
from pz_1.helpers import running, unused_port
lazy from lab_4.tcp_server import Address


@pytest.fixture
def upload_dir(tmp_path: Path) -> Path:
    return tmp_path / "received"


@pytest.fixture
def server_address(upload_dir: Path) -> Generator[Address]:
    with running(FileServer("127.0.0.1", 0, upload_dir)) as address:
        yield address


@pytest.fixture
def text_file(tmp_path: Path) -> Path:
    path = tmp_path / "notes.txt"
    path.write_text("first line\nsecond line\n", encoding="utf-8")
    return path


def address_args(address: Address) -> list[str]:
    return ["--host", address[0], "--port", str(address[1])]


def test_send_file_uploads_content(server_address: Address, text_file: Path, upload_dir: Path) -> None:
    assert file_client.send_file(text_file, *server_address) == "OK notes.txt"
    assert (upload_dir / "notes.txt").read_bytes() == text_file.read_bytes()


def test_send_file_returns_server_error(server_address: Address, tmp_path: Path) -> None:
    binary = tmp_path / "image.png"
    binary.write_bytes(b"\x89PNG\xff\xfe")
    assert file_client.send_file(binary, *server_address) == "ERROR file is not UTF-8 text"


def test_parse_args_uses_default_address() -> None:
    args = file_client.parse_args(["notes.txt"])
    assert (args.path, args.host, args.port) == (Path("notes.txt"), HOST, PORT)


def test_parse_args_reads_custom_address() -> None:
    args = file_client.parse_args(["notes.txt", "--host", "10.0.0.5", "--port", "6000"])
    assert (args.host, args.port) == ("10.0.0.5", 6000)


def test_main_prints_server_reply(
    server_address: Address, text_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    file_client.main([str(text_file), *address_args(server_address)])
    assert capsys.readouterr().out.endswith("Server replied: OK notes.txt\n")


def test_main_exits_with_error_on_rejected_file(
    server_address: Address, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    binary = tmp_path / "image.png"
    binary.write_bytes(b"\xff")
    with pytest.raises(SystemExit) as exit_info:
        file_client.main([str(binary), *address_args(server_address)])
    assert exit_info.value.code == 1
    assert capsys.readouterr().out.endswith("Server replied: ERROR file is not UTF-8 text\n")


def test_main_exits_when_file_is_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    with pytest.raises(SystemExit, match=f"File not found: {missing}"):
        file_client.main([str(missing)])


def test_main_exits_when_file_is_too_large(text_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(file_client, "MAX_FILE_SIZE", 5)
    with pytest.raises(SystemExit, match="File is larger than 5 bytes"):
        file_client.main([str(text_file)])


def test_main_exits_when_server_is_down(text_file: Path) -> None:
    port = unused_port()
    with pytest.raises(SystemExit, match=f"File server is not running on 127.0.0.1:{port}"):
        file_client.main([str(text_file), "--port", str(port)])


def test_main_exits_when_connection_breaks(text_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(file_client, "send_file", Mock(side_effect=ConnectionResetError("reset by peer")))
    with pytest.raises(SystemExit, match="Upload failed: reset by peer"):
        file_client.main([str(text_file)])


def test_main_rejects_file_name_with_line_break(tmp_path: Path) -> None:
    path = tmp_path / "bad\nname.txt"
    path.write_text("data", encoding="utf-8")
    with pytest.raises(SystemExit, match="File name must not contain line breaks"):
        file_client.main([str(path)])
