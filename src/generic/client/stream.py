import socket
import threading
import json

from uuid import uuid4
from src.generic.types import *


def create_uuid(): 
    return uuid4()


class Stream(socket.socket): 
    def __init__(self, address : Address, *args) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_STREAM, *args)
        self.connect(address)

        self.address = address
        self._action_response = []
        rec_messages_thread = threading.Thread(target=self._recv_messages, args=(self,))
        rec_messages_thread.daemon = True
        rec_messages_thread.start()

    def connect(self, address: Address) -> None:
        return super().connect((address.ip, address.port)) 


    def _send_action(self, action, **kwargs): # TODO: shitty way of sending msg 
        kwargs["action"] = action
        kwargs["message_uuid"] = create_uuid()
    
        json_dump = json.dumps(kwargs) 
        self.sendall(f"{str(len(json_dump)).zfill(4)}{json_dump}".encode())

        return kwargs["message_uuid"]
    

    def _recv_messages(self): # TODO: shitty way of receiving a msg 
        while True: 
            length = int(self.recv(4).decode())
            data = json.load(self.recv(length)) 
            self._messages.append(data)


    def _find_response(self, uuid, retries=1): 
        for _ in range(retries): 
            for message in self._messages:
                if message.get("message_uuid") == uuid: 
                    self._action_response.remove(message)
                    return message
        return Status.NOT_FOUND


    def send_action(self, action, retries=1, **kwargs): 
        uuid = self._send_action(action, **kwargs)

        return self._find_response(uuid, retries) 
    

class SecureStream(socket.socket):
    def __init__(self, address : Address, *args) -> None:
        super().__init__(address)    


class StreamAuthorized(SecureStream): 
    def __init__(self, address: Address, key) -> None:
        super().__init__(address)
        self._key = key 
    
    def send_action(self, action, *kwargs): 
        kwargs['key'] = self._key 
        super().send_action(action, kwargs)

