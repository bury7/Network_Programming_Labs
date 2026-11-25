lazy import socket

from lab_4.tcp_server import Address, TcpServer

HOST = "127.0.0.1"
PORT = 50007
BUFFER_SIZE = 1024


class EchoServer(TcpServer):
    name = "Echo server"

    def handle(self, connection: socket.socket, address: Address) -> None:
        print(f"Connected by {address[0]}:{address[1]}")
        while data := connection.recv(BUFFER_SIZE):
            connection.sendall(data)


if __name__ == "__main__":
    EchoServer(HOST, PORT).run()
