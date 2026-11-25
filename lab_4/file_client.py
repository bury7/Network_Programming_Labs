import argparse
import socket
import sys
from pathlib import Path

from lab_4.file_server import HOST, MAX_FILE_SIZE, PORT


def send_file(path: Path, host: str = HOST, port: int = PORT) -> str:
    data = path.read_bytes()
    with socket.create_connection((host, port)) as client:
        client.sendall(f"{path.name}\n{len(data)}\n".encode() + data)
        client.shutdown(socket.SHUT_WR)
        with client.makefile("r", encoding="utf-8") as stream:
            return stream.readline().strip()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a text file to the file server.")
    parser.add_argument("path", type=Path, help="text file to send")
    parser.add_argument("--host", default=HOST, help=f"server host (default: {HOST})")
    parser.add_argument("--port", type=int, default=PORT, help=f"server port (default: {PORT})")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if not args.path.is_file():
        sys.exit(f"File not found: {args.path}")
    if "\n" in args.path.name:
        sys.exit("File name must not contain line breaks")
    if args.path.stat().st_size > MAX_FILE_SIZE:
        sys.exit(f"File is larger than {MAX_FILE_SIZE} bytes")
    try:
        reply = send_file(args.path, args.host, args.port)
    except ConnectionRefusedError:
        sys.exit(f"File server is not running on {args.host}:{args.port}")
    except OSError as error:
        sys.exit(f"Upload failed: {error}")
    print(f"Server replied: {reply}")
    if not reply.startswith("OK"):
        sys.exit(1)


if __name__ == "__main__":
    main()
