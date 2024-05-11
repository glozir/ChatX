from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List
from __future__ import annotations

class ContentType(Enum): 
    IMAGE =  1
    GIF = 2 
    STRING = 3

class ActionType(Enum): 
    CreateThread = 1 
    CreateSession = 2  
    Authenticate = 3 
    CreateUser = 4 
    GetSessions = 5
    GetThreads = 6
    GetContent = 7 

class Status(Enum):
    NOT_FOUND = 2 
    SUCCESS = 1 
    FAILURE = 0 
    
@dataclass
class Address:
    ip : str
    port : int


class GenericDataclass: 
    @dataclass
    class Content: 
        content_data : bytes 
        content_type : ContentType 
        user : str  
        upload_time : datetime  
        num_of_threads : int
        threads : List[GenericDataclass.Thread] | None = None 

    @dataclass
    class Session:
        uuid : bytes
        content : GenericDataclass.Content

    @dataclass
    class Thread(Session): 
        parent : GenericDataclass.Session | GenericDataclass.Thread 

    @dataclass
    class User:
        name: str
        hashed_password: bytes




    
    