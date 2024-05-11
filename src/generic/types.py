from enum import Enum
from dataclasses import dataclass
from datetime import datetime

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

@dataclass
class Content: 
    content_data : bytes 
    content_type : ContentType 
    user : str  
    upload_time : datetime  
    num_of_threads : int 