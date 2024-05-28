from enum import Enum
from functools import wraps

from ..generic.session import Session, Thread
from ..generic.types import Dataclass

class AuthenticationLevel(Enum):
    Protected = 0
    Open = 1 
    Restricted = 2 


class SessionHandler(Session):
    """Class SessionHandler handles the session management for the server side"""

    def __init__(self, uuid=None, content: Dataclass.Content = None, **kwargs) -> None:
        super().__init__(uuid, content, **kwargs)

        self.users = {}
        self.sessions: Thread = {}

    @staticmethod
    def Authenticated(level : AuthenticationLevel): 
        def decorator(func):
            @wraps(func)
            def wrapper(self, key, **kwargs):

                return None
            return wrapper
        return decorator
    
