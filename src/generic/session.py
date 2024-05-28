""" Base session """
from __future__ import annotations
from typing import Union, List

from ..generic.types import Dataclass
from .utils import create_uuid


class Session(object):
    """ Base Session class, holds its content and child threads"""

    def __init__(self, uuid=None, content: Dataclass.Content = None) -> None:
        if not uuid:
            uuid = create_uuid()
        self.uuid = uuid
        self.threads = []
        self.content: Dataclass.Content = content

    def append(self, thread: Thread) -> None:
        """ Append a thread to the session threads list."""
        self.threads.append(thread)

    def create_thread(self, content: Dataclass.Content = None) -> None:
        """ Create a thread with optional content argument."""
        self.append(Thread(self, content))

    def get_content(self) -> Union[Dataclass.Content | None]:
        """ Returns the content property of the session."""
        return self.content

    def get_threads(self) -> Union[List[Thread] | None]:
        """ Returns the threads property of the session."""
        return self.threads

# TODO: create  UUID base on parent UUID so it would lookup in log(n) time


class Thread(Session):
    """ Base Thread class, child of parent Thread or Session, 
        holds its own child threads and content"""

    def __init__(self, parent: Thread = None, uuid=None,
                 content: Dataclass.Content = None, **kwargs) -> None:
        super().__init__(uuid, content, **kwargs)

        self.parent = parent
