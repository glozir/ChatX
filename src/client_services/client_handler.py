""" client handler is responsible for the communication of the client side with the server"""
from __future__ import annotations
from typing import Union, List

from ..generic.types import Dataclass, ActionType, Status, Method
from ..generic.client.http_client import httpClient, httpClientAuthorized
from ..generic.session import Session, Thread


class Xclient(httpClient):
    """ Class Xclient is responsible for handling the client side communication"""

    def __init__(self, **kwargs) -> None:
        httpClient.__init__()

        self.username: str = None
        self.handler: SessionHandler = None

    def authenticate(self, username: str, password: str) -> Status:
        """ Sends an authentication request to the server with the user credentials 

        Args:
            username (str): the username of the client user
            password (str): the password of the client user

        Returns:
            Status: returns the status of the operation, 
            Success if the server returns the session key, 
            Failure if the server doesn't return the session key  
        """
        key = self.send_action(ActionType.Authenticate, Method.GET, {
            "password": password,
            "username": username
        })
        if key == Status.FAILURE:
            return Status.FAILURE

        self.username = username
        self.handler = SessionHandler(key)
        return Status.SUCCESS

    def create_user(self, username, password):
        """ Sends a create user requests to the server with newly created credentials 

        Args:
            username (str): the username of the client user
            password (str): the password of the client user

        Returns:
            Status: returns the status of the operation, 
            Success if the server returns the session key, 
            Failure if the server doesn't return the session key  
        """
        response = self.send_action(ActionType.CreateUser, Method.GET, {
            "password": password,
            "username": username
        })
        if not response:
            return Status.FAILURE

        self.username = username
        self.handler = SessionHandler(response)
        return Status.SUCCESS


class SessionHandler(httpClientAuthorized):
    """ Class SessionHandler is responsible for handling session communication from the client 
        side and stores all of the client threads
        """

    def __init__(self, key: str, **kwargs) -> None:
        super().__init__(key, **kwargs)

        self.sessions: ClientSession = []

    def create_session(self, content: Dataclass.Content) -> Status:
        """ Sends a Create Session request to the server with the session content

        Args:
            content (Dataclass.Content): The content of the Session to be created   

        Returns:
            Status: returns the status of the operation,
            Success if the server returns the server uuid,
            Failure if the server doesn't return the server uuid 
        """
        response = self.send_action(ActionType.CreateSession, Method.POST, **content)

        if not response.get("session_uuid"):
            return Status.FAILURE

        self.append(ClientSession(self, response["session_uuid"], content))
        return Status.SUCCESS

    def get_sessions(self, number: int = 10) -> Union[List[ClientSession], Status]:
        """ Sends a get Sessions request to the server with the number of requested sessions

        Args:
            number (int): the number of the requested sessions    

        Returns:
            Status: returns the status of the operation,
            Success if the server returns the sessions,
            Failure if the server doesn't return the sessions  
        """
        response = self.send_action(ActionType.GetSessions, Method.GET, {
            'number': number
        })


        for session in response:
            if not session.get("uuid"):
                return Status.FAILURE
            self.append(ClientSession(self, session["uuid"]))

        return self.sessions

    def append(self, session):
        """ Append to the Object sessions list"""
        self.sessions.append(session)


class ClientSession(Session):
    """ Class ClientSession is responsible for handling the session from the client side"""

    def __init__(self, handler: SessionHandler, uuid=None,
                 content: Dataclass.Content = None, **kwargs):
        super().__init__(uuid, content, **kwargs)

        self.handler = handler

    def send_action(self, action, method, params, **kwargs):
        """ sends action to server with respective kwargs."""
        return self.handler.send_action(action, method, params, **kwargs)

    def create_thread(self, content: Dataclass.Content) -> Status:
        response = self.send_action(ActionType.CreateThread, Method.POST, params={"parent_uuid": self.uuid},
            **content)

        if not response:
            return Status.FAILURE

        self.append(ClientThread(self.handler, self,
                    response, content))

        return Status.SUCCESS


    def get_thread(self):
        response = self.send_action(ActionType.GetThread, Method.GET, **{
            "uuid": self.uuid,
        })

        if not response:
            return Status.NOT_FOUND
        
        self.append(ClientThread(
            self.handler, self, response["uuid"], response["content"]))

        return self.threads


class ClientThread(Thread, ClientSession):
    """ class ClientThread is responsible for handling the thread from the client side"""

    def __init__(self, handler, parent, uuid=None, content: Dataclass.Content = None, **kwargs):
        super().__init__(parent, uuid, content ** kwargs)
        super().__init__(handler, **kwargs)


if __name__ == "__main__":
    pass
