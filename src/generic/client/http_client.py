""" Base stream class for client side that abstracts socket communications"""
import requests

from ..types import Dataclass, Status, ActionType
from ..utils import create_uuid


class httpClient(requests.Session):
    """ Class Client.Stream wraps the client socket and abstracts the communication
        between the client and the server for easier handling"""

    def __init__(self) -> None:
        super().__init__()

        self._messages = {}

        rec_messages_thread = threading.Thread(
            target=self._recv_messages, args=(self,))
        rec_messages_thread.daemon = True
        rec_messages_thread.start()

    def _connect(self, address: Dataclass.Address) -> None:
        return super().connect((address.ip, address.port))

    # TODO: shitty way of sending msg
    def _send_action(self, action: ActionType, **kwargs):
        kwargs["action"] = action
        kwargs["message_uuid"] = create_uuid()

        json_dump = json.dumps(kwargs)
        length = str(len(json_dump)).zfill(4)
        self.sendall(f"{length}{json_dump}".encode())

        return kwargs["message_uuid"]

    def _recv_messages(self):  # TODO: shitty way of receiving a msg
        while True:
            length = int(self.recv(4).decode())
            data = json.load(self.recv(length))
            if not data.get("message_uuid"):
                continue

            message_uuid = data["message_uuid"]
            self._messages[message_uuid] = data

    def _find_response(self, uuid, retries=1):
        for _ in range(retries):
            if self._messages.get(uuid):
                return self._messages.pop(uuid)
        return Status.NOT_FOUND

    def send_action(self, action: Status, retries=1, **kwargs) -> dict:
        """ sends an action to the server with its respective parameters and returns the response

        Args:
            action (Status): The action that the client requests from the server
            retries (int, optional): The amount of retries the function should do, Defaults to 1
            kwargs (dict): a dictionary containing the action parameters 

        Returns:
            dict: The dictionary contacting the response
        """
        uuid = self._send_action(action, **kwargs)

        return self._find_response(uuid, retries)


class SecureStream(Stream):  # TODO: not finished
    """ Class SecureStream wraps the Stream class in TLS encryption"""


class StreamAuthorized(SecureStream):
    """ Class StreamAuthorized wraps the Stream and adds key verification to messages"""

    def __init__(self, key, address: Dataclass.Address, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self._key = key

    def send_action(self, action: ActionType, retries: int = 1, **kwargs) -> dict:
        kwargs['key'] = self._key

        return super().send_action(action, retries, **kwargs)
