from src.generic.session import Thread, Session
from src.generic.types import Dataclass


class SessionHandler(Session):
    def __init__(self, uuid=None, content: Dataclass.Content = None, **kwargs) -> None:
        super().__init__(uuid, content, **kwargs)
