import socket
from abc import ABC, abstractmethod

type Address = tuple[str, int]

CLIENT_TIMEOUT = 30


class TcpServer(ABC):
    name = "TCP server"

    def __init__(self, host: str, port: int, timeout: float = CLIENT_TIMEOUT) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    @abstractmethod
    def handle(self, connection: socket.socket, address: Address) -> None: ...

    def handle_client(self, connection: socket.socket, address: Address) -> None:
        with connection:
            connection.settimeout(self.timeout)
            self.handle(connection, address)

    def serve_forever(self, listener: socket.socket) -> None:
        while True:
            connection, address = listener.accept()
            try:
                self.handle_client(connection, address)
            except OSError as error:
                print(f"{address[0]}:{address[1]} connection error: {error}")

    def run(self) -> None:
        with socket.create_server((self.host, self.port)) as listener:
            print(f"{self.name} is listening on {self.host}:{self.port}, press Ctrl+C to stop")
            try:
                self.serve_forever(listener)
            except KeyboardInterrupt:
                print("\nServer stopped")
