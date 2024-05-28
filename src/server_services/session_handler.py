from ..generic.session import Session, Thread
from ..generic.types import Dataclass


class SessionHandler(Session):
    """Class SessionHandler handles the session management for the server side"""

    def __init__(self, uuid=None, content: Dataclass.Content = None, **kwargs) -> None:
        super().__init__(uuid, content, **kwargs)

        self.users = []
        self.sessions: Thread = []
