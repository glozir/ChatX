from bcrypt import hashpw, gensalt, checkpw
from typing import List, Union

from ..generic.types import Dataclass, ActionType, Status
from ..generic.database.database_handler import AsyncMongoDBClient
from ..generic.utils import create_uuid
from ..server_services.action_handler import Xhandler, AuthenticationLevel

class Xserver(Xhandler):
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
    async def authenticate(self, username, password) -> str:
        user = await self.database_handler.find_user_by_name(username)
        if not user:
            return Status.FAILURE

        if not checkpw(bytes(password, encoding="utf-8"), user.hashed_password):
            return Status.FAILURE

        return self.assign_key(username)

    @Xhandler.GET(ActionType.CreateUser)
    async def create_user(self, username : str, password : str) -> str:
        user = await self.database_handler.find_user_by_name(username)
        if user: 
            return Status.FAILURE

        await self.database_handler.add_user(Dataclass.User(username, hashpw(bytes(password, encoding="utf-8"), gensalt())))
        return self.assign_key(username)

    @Xhandler.POST(ActionType.CreateSession, protection_level=AuthenticationLevel.PROTECTED)
    async def create_session(self, key : str, content : Dataclass.Content) -> str:
        username = self.users.get(key)
        if not username:
            return Status.FAILURE
        if content.username != username:
            return Status.FAILURE
        uuid = create_uuid()
        session = Dataclass.Session(uuid, content)
        await self.database_handler.add_session(session)

        return uuid 

    @Xhandler.POST(ActionType.CreateThread)
    async def create_thread(self, key : str, content : Dataclass.Content, parent_uuid : str) -> str:
        username = self.users.get(key)
        if not username:
            return Status.FAILURE
        if content.username != username:
            return Status.FAILURE
        uuid = create_uuid()
        thread = Dataclass.Thread(uuid, content, parent_uuid)
        await self.database_handler.add_thread(thread)

        return uuid

    @Xhandler.GET(ActionType.GetSession)
    async def get_session_by_uuid(self, uuid : str) -> Dataclass.Session:
        return await self.database_handler.find_session_by_uuid(uuid)

    @Xhandler.GET(ActionType.GetThread)
    async def get_thread_by_uuid(self, uuid : str) -> Dataclass.Thread:
        return await self.database_handler.find_session_by_uuid(uuid)
    
    @Xhandler.GET(ActionType.GetSessions)
    async def get_sessions(self, number : int = 5) -> List[Dataclass.Session]: 
        return await self.database_handler.get_sessions(number)


