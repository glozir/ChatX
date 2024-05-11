import socket 
import datetime
import logging
import json 
import threading

from uuid import uuid4 
from src.generic.types import * 
from src.generic.client.stream import SecureStream, StreamAuthorized
from src.generic.session import Session

class Xclient(SecureStream):
    def __init__(self, address: Address, *args) -> None:
        super().__init__(address, *args)
    
        self.username = None
        self.handler = None

    def authenticate(self, username, password):
        key = self.send_action(ActionType.Authenticate, {
            "password" : password, 
            "username" : username 
        })
        if not key: 
            return Status.FAILURE
        
        self.username = username
        self.handler = Handler(self.address, key) 
        return Status.SUCCESS

    def create_user(self, username, password): 
        response = self.send_action(ActionType.CreateUser, {
            "password" : password, 
            "username" : username 
        }) 
        if not response.get("key"): 
            return Status.FAILURE
        
        self.username = username
        self.handler = Handler(self.address, response.get("key")) 
        return Status.SUCCESS       
    

class Handler(StreamAuthorized):
    def __init__(self, address : Address, key) -> None:
        super().__init__(address, key)

        self.sessions = []


    def create_session(self, content_type, content): 
        response = self.send_action(ActionType.CreateSession, {
            "content_type" : content_type, 
            "content" : content
        })

        if not response.get("session_uuid"):
            return Status.FAILURE

        self.append(Session(response["session_uuid"], self)) 
        return Status.SUCCESS
    
    def get_sessions(self, number=10): 
        response = self.send_action(ActionType.GetSessions, { 
            'number_of_sessions' : number 
        })

        if not response.get("sessions"): 
            return Status.FAILURE
        
        for session in response["sessions"]: 
            if not session.get("session_uuid"): 
                return Status.FAILURE
            self.append(Session(session["session_uuid"], self))
    
    def append(self, session): 
        self.sessions.append(session)


class ClientSession(Session): 
    def __init__(self, handler, uuid, content=None, content_type=None, user=None, upload_time=None, num_of_threads=None):
        super().__init__(uuid, content, content_type, user, upload_time, num_of_threads)

        self.handler = handler

    def send_action(self, action, **kwargs): 
        self.handler.send_action(action, **kwargs)

    def create_thread(self, content_type, content): 
        response = self.send_action(ActionType.CreateThread, {
            "content_type" : content_type, 
            "content" : content, 
            "parent_uuid" : self.uuid,
        })

        if not response.get("thread_uuid"): 
            return Status.FAILURE
        
        self.append(ClientThread(response["thread_uuid"], self))
        return Status.SUCCESS
    
    def get_content(self):
        if not all(super().get_content()): 
            response = self.send_action(ActionType.GetContent, {
                "content_uuid" : self.uuid
            })

            if not all(response.get("content"), response.get("content_type"), response.get("user")
                    / response.get("upload_time"), response.get("num_of_threads")): 
                return Status.FAILURE
            
            self.content = response["content"]
            self.content_type = response["content_type"]
            self.user = response["user"]
            self.upload_time = response["upload_time"]
            self.num_of_threads = response["num_of_threads"]

            return super().get_content()
        return super().get_content()
    
    def get_threads(self): 
        response = self.send_action(ActionType.GetThreads, {
            "parent_uuid" : self.uuid, 
        })

        if not response.get("threads"): 
            return Status.NOT_FOUND
        
        for thread in response["threads"]: 
            self.append(ClientThread(thread["uuid"], self))
        return super().get_threads()


class ClientThread(ClientSession):
    def __init__(self, uuid, parent):
        super().__init__(uuid)
        
        self.parent = parent


if __name__ == "__main__":
    x = Xclient(Address("localhost", "1337"))
    x.create_user("popisgod", "123456")

    handler = x.handler
    handler.create_session(ContentType.STRING, "hello world")

    handler.get_sessions()




