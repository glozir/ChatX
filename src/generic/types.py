""" Types """
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


class ContentType(Enum):
    IMAGE = 1
    GIF = 2
    STRING = 3


class ActionType(Enum):
    CreateThread = 1
    CreateSession = 2
    Authenticate = 3
    CreateUser = 4
    GetSession = 5
    GetThread = 6
    GetSessions = 7
    GetContent = 8 

class Method(Enum): 
    GET = 0 
    POST = 1

class Status(Enum):
    NOT_FOUND = 2
    SUCCESS = 1
    FAILURE = 0


class Dataclass:
    @dataclass
    class Address:
        ip: str
        port: int

    @dataclass
    class Content:
        content_data: bytes
        content_type: ContentType
        username: str
        upload_time: datetime
        num_of_threads: int
        threads_uuid: List[bytes] | None = None

    @dataclass
    class Session:
        uuid: bytes
        content: Dataclass.Content

    @dataclass
    class Thread(Session):
        parent_uuid: bytes | None

    @dataclass
    class User:
        name: str
        hashed_password: bytes
