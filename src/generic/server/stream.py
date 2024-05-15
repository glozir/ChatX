""" Base stream class for server side that abstracts socket communications"""
import socket
import json
import select

from src.generic.types import Status, Dataclass


class StreamServer(socket.socket):
    """ Base Stream class
      for starting the connection between the server and the clients and processing requests """

    def __init__(self, address: Dataclass.Address) -> None:
        super().__init__()

        self.inputs = [self]
        self.clients = []
        self.readable = []
        self.writable = []

        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((address.ip, address.port))
        self.listen()

    def run(self):
        while True:
            self.readable, self.writable, _ = select.select(
                self.inputs, self.clients, [])

            for sock in self.readable:
                if not sock is self:
                    self.recv_action(sock)

                client_sock, _ = self.accept()
                self.inputs.append(client_sock)
                self.clients.append(client_sock)

    def recv_action(self, sock):
        length = int(sock.recv(4).decode())
        data = json.loads(sock.recv(length))

        return sock, data

    def send_message(self, sock, **kwargs):
        if not sock in self.writable:
            return Status.FAILURE

        json_dump = json.dumps(kwargs)
        sock.sendall(f"{str(len(json_dump)).zfill(4)}{json_dump}")
        return Status.SUCCESS
