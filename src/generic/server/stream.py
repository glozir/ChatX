import socket
import threading
import json
import select 

from src.generic.types import *
from src.generic.utils import create_uuid

class StreamServer(socket.socket): 
    def __init__(self, address) -> None:
        super().__init__(socket.AF_INET,  socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((address.ip, address.port))
        self.listen()


        self.inputs = [self]
        self.clients = []
    
    def run(self): 
        while True: 
            self.readable, self.writable, _ = select.select(self.inputs, self.clients, [])

            for sock in self.readable: 
                if not sock is self:
                    self.recv_action(sock)

                client_sock, _ = self.accept()
                self.inputs.append(client_sock)
                self.clients.append(client_sock)
        
    def recv_action(self, sock): 
        length = int(sock.recv(4).decode()) 
        data = json.load(sock.recv(length))

        return sock, data
    
    def send_message(self, sock, **kwargs): 
        if not sock in self.writable: 
            return Status.FAILURE
        
        json_dump = json.dump(kwargs)
        sock.sendall(f"{str(len(json_dump)).zfill(4)}{json_dump}")
        return Status.SUCCESS
