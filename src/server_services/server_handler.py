from bcrypt import hashpw, gensalt, checkpw

from ..generic.types import Dataclass, ActionType, Status
from ..generic.database.database_handler import AsyncMongoDBClient
from ..generic.utils import create_uuid
from ..server_services.session_handler import SessionHandler, AuthenticationLevel
from ..server_services.action_handler import Xhandler

class Xserver(SessionHandler):
    def __init__(self, db_url=None, **kwargs) -> None:
        super().__init__(**kwargs)

        self.database_handler = AsyncMongoDBClient(db_url)
        self.route_handler = Xhandler.ROUTER

        Xhandler.register_routes(self)

    def assign_key(self, username):
        key = create_uuid() 
        self.users[key] = username
        return key

    @Xhandler.GET(ActionType.Authenticate)
    async def authenticate(self, username, password):
        user = await self.database_handler.find_user_by_name(username)
        if not user:
            return Status.FAILURE

        if not checkpw(bytes(password, encoding="utf-8"), user.hashed_password):
            return Status.FAILURE

        return self.assign_key(username)

    @Xhandler.GET(ActionType.CreateUser)
    async def create_user(self, username : str, password : str):
        user = await self.database_handler.find_user_by_name(username)
        if user:
            return Status.FAILURE

        await self.database_handler.add_user(Dataclass.User(username, hashpw(bytes(password, encoding="utf-8"), gensalt())))
        return self.assign_key(username)

    @Xhandler.POST(ActionType.CreateSession, authenticate=AuthenticationLevel.Protected)
    async def create_session(self, username : str, content : Dataclass.Content):
        pass 

    @Xhandler.GET(ActionType.CreateThread)
    async def create_thread(self):
        pass

    @Xhandler.GET(ActionType.GetSessions)
    async def get_sessions(self):
        pass

    @Xhandler.GET(ActionType.GetThreads)
    async def get_threads(self):
        pass

    @Xhandler.GET(ActionType.GetContent)
    async def get_content(self):
        pass
