""" client handler is responsible for the communication of the client side with the server"""
from __future__ import annotations
from typing import Union, List

from ..generic.types import Dataclass, ActionType, Status
from ..generic.client.http_client import httpClient
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
        key = self.send_action(ActionType.Authenticate, {
            "password": password,
            "username": username
        })
        if not key:
            return Status.FAILURE

        self.username = username
        self.handler = SessionHandler(self.address, key)
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
        response = self.send_action(ActionType.CreateUser, {
            "password": password,
            "username": username
        })
        if not response.get("key"):
            return Status.FAILURE

        self.username = username
        self.handler = SessionHandler(self.address, response.get("key"))
        return Status.SUCCESS


class SessionHandler(StreamAuthorized):
    """ Class SessionHandler is responsible for handling session communication from the client 
        side and stores all of the client threads
        """

    def __init__(self, key: str, address: Dataclass.Address, **kwargs) -> None:
        super().__init__(key, address, **kwargs)

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
        response = self.send_action(ActionType.CreateSession, **{
            "content": content
        })

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
        response = self.send_action(ActionType.GetSessions, {
            'number_of_sessions': number
        })

        if not response.get("sessions"):
            return Status.FAILURE

        for session in response["sessions"]:
            if not session.get("session_uuid"):
                return Status.FAILURE
            self.append(ClientSession(self, session["session_uuid"]))

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

    def send_action(self, action, **kwargs):
        """ sends action to server with respective kwargs."""
        return self.handler.send_action(action, **kwargs)

    def create_thread(self, content: Dataclass.Content) -> Status:
        response = self.send_action(ActionType.CreateThread, **{
            "content": content,
            "parent_uuid": self.uuid,
        })

        if not response.get("uuid"):
            return Status.FAILURE

        self.append(ClientThread(self.handler, self,
                    response["uuid"], content))

        return Status.SUCCESS

    def get_content(self):
        if not self.content:
            response = self.send_action(ActionType.GetContent, **{
                "uuid": self.uuid
            })
            response = response.get("content")
            if not response:
                return Status.FAILURE

            self.content = Dataclass.Content(**response)

            return self.content
        return self.content

    def get_threads(self):
        response = self.send_action(ActionType.GetThreads, **{
            "uuid": self.uuid,
        })

        if not response.get("threads"):
            return Status.NOT_FOUND
        for thread in response["threads"]:
            self.append(ClientThread(
                self.handler, self, thread["uuid"]))

        return self.threads


class ClientThread(Thread, ClientSession):
    """ class ClientThread is responsible for handling the thread from the client side"""

    def __init__(self, handler, parent, uuid=None, content: Dataclass.Content = None, **kwargs):
        super().__init__(parent, uuid, content ** kwargs)
        super().__init__(handler, **kwargs)


if __name__ == "__main__":
    pass
