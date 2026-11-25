import argparse
import socket
import sys

from lab_4.echo_server import BUFFER_SIZE, HOST, PORT


def echo(message: str, host: str = HOST, port: int = PORT) -> str:
    with socket.create_connection((host, port)) as client:
        client.sendall(message.encode())
        client.shutdown(socket.SHUT_WR)
        return b"".join(iter(lambda: client.recv(BUFFER_SIZE), b"")).decode()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a message to the echo server.")
    parser.add_argument("message", nargs="?", default="Hello, world", help="text to send")
    parser.add_argument("--host", default=HOST, help=f"server host (default: {HOST})")
    parser.add_argument("--port", type=int, default=PORT, help=f"server port (default: {PORT})")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    try:
        reply = echo(args.message, args.host, args.port)
    except ConnectionRefusedError:
        sys.exit(f"Echo server is not running on {args.host}:{args.port}")
    except OSError as error:
        sys.exit(f"Connection failed: {error}")
    print(f"Sent:     {args.message}")
    print(f"Received: {reply}")


if __name__ == "__main__":
    main()
