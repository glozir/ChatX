""" Base stream class for client side that abstracts socket communications"""
import requests

from ..types import Dataclass, Status, ActionType, Method
from ..utils import create_uuid

SERVER_ADDRESS = "http://0.0.0.0:1337/"

class httpClient(requests.Session):
    """ Class Client.Stream wraps the client socket and abstracts the communication
        between the client and the server for easier handling"""

    def __init__(self) -> None:
        super().__init__()



    def send_action(self, action: Status, method : Method, params=None, **kwargs) -> dict:
        """ sends an action to the server with its respective parameters and returns the response

        Args:
            action (Status): The action that the client requests from the server
            retries (int, optional): The amount of retries the function should do, Defaults to 1
            kwargs (dict): a dictionary containing the action parameters 

        Returns:
            dict: The dictionary contacting the response
        """
        if method == Method.POST: 
            res = self.post(f"{SERVER_ADDRESS}/{action.name}", params=params, json=kwargs)
        elif method == Method.GET:
            res = self.get(f"{SERVER_ADDRESS}/{action.name}", params=kwargs)
        
        return res.json()
        


class httpClientAuthorized(httpClient):

    def __init__(self, key, **kwargs) -> None:
        super().__init__(**kwargs)
        self._key = key

    def send_action(self, action: ActionType, method : Method, params : dict=dict(), **kwargs) -> dict:
        return super().send_action(action, method, params.update({"key" : self._key}) , **kwargs)