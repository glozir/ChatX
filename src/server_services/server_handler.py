from bcrypt import hashpw, gensalt, checkpw

from ..generic.types import Dataclass, ActionType, Status
from ..generic.database.database_handler import AsyncMongoDBClient
from ..generic.utils import create_uuid
from ..server_services.session_handler import SessionHandler
from ..server_services.action_handler import Xhandler


class Xserver(SessionHandler):
    def __init__(self, db_url=None, **kwargs) -> None:
        SessionHandler.__init__(**kwargs)

        self.database_handler = AsyncMongoDBClient(db_url)
        self.route_handler = Xhandler.ROUTER

    def assign_key(self, username):
        key = create_uuid()  # TODO: change this logic
        self.users[key] = username
        return key

    @Xhandler(ActionType.Authenticate)
    async def authenticate(self, username, password):
        user = await self.database_handler.find_user_by_name(username)
        if not user:
            return Status.FAILURE

        if not checkpw(password, user.hashed_password):
            return Status.FAILURE

        return self.assign_key(username)

    @Xhandler(ActionType.CreateUser)
    async def create_user(self, username, password):
        user = await self.database_handler.find_user_by_name(username)
        if user:
            return Status.FAILURE

        await self.database_handler.add_user(Dataclass.User(username, hashpw(password, gensalt())))
        return self.assign_key(username)

    @Xhandler(ActionType.CreateSession)
    async def create_session(self, key, content):
        username = self.users[key]

    @Xhandler(ActionType.CreateThread)
    async def create_thread(self):
        pass

    @Xhandler(ActionType.GetSessions)
    async def get_sessions(self):
        pass

    @Xhandler(ActionType.GetThreads)
    async def get_threads(self):
        pass

    @Xhandler(ActionType.GetContent)
    async def get_content(self):
        pass
