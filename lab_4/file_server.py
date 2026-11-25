from pathlib import Path
lazy import socket

from lab_4.tcp_server import CLIENT_TIMEOUT, Address, TcpServer

HOST = "127.0.0.1"
PORT = 50008
UPLOAD_DIR = Path(__file__).with_name("received")
MAX_HEADER_LENGTH = 1024
MAX_FILE_SIZE = 10 * 1024 * 1024


def is_text(data: bytes) -> bool:
    try:
        data.decode()
    except UnicodeDecodeError:
        return False
    return True


class FileServer(TcpServer):
    name = "File server"

    def __init__(self, host: str, port: int, upload_dir: Path, timeout: float = CLIENT_TIMEOUT) -> None:
        super().__init__(host, port, timeout)
        self.upload_dir = upload_dir

    def handle(self, connection: socket.socket, address: Address) -> None:
        reply = self.receive_file(connection)
        print(f"{address[0]}:{address[1]} {reply}")
        connection.sendall(f"{reply}\n".encode())

    def receive_file(self, connection: socket.socket) -> str:
        with connection.makefile("rb") as stream:
            name = Path(stream.readline(MAX_HEADER_LENGTH).decode(errors="replace").strip()).name
            size_line = stream.readline(MAX_HEADER_LENGTH).strip()
            if name in {"", ".", ".."} or "\0" in name:
                return "ERROR invalid file name"
            if not size_line.isdigit() or int(size_line) > MAX_FILE_SIZE:
                return f"ERROR file size must be a number of bytes up to {MAX_FILE_SIZE}"
            size = int(size_line)
            data = stream.read(size)

        if len(data) != size:
            return "ERROR connection closed before the whole file was received"
        if not is_text(data):
            return "ERROR file is not UTF-8 text"

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        (self.upload_dir / name).write_bytes(data)
        return f"OK {name}"

    def run(self) -> None:
        print(f"Files are saved to {self.upload_dir}")
        super().run()


if __name__ == "__main__":
    FileServer(HOST, PORT, UPLOAD_DIR).run()
