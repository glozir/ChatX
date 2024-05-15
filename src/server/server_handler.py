from bcrypt import hashpw, gensalt, checkpw

from src.generic.types import Dataclass, ActionType, Status
from src.generic.server.stream import StreamServer
from src.generic.database import AsyncMongoDBClient
from src.generic.utils import create_uuid
from chat_client.src.server.session_handler import SessionHandler
from src.server.action_handler import Xhandler


class Xserver(StreamServer, SessionHandler):
    def __init__(self, address=None, db_url=None, **kwargs) -> None:
        super(StreamServer).__init__(address)
        super(SessionHandler).__init__(**kwargs)

        self.database_handler = AsyncMongoDBClient(db_url)
        self.handler = Xhandler

    async def recv_action(self, sock):
        return await self.handle_action(sock, super().recv_action(sock))

    async def handle_action(self, sock, data):
        if not data.get("action_type"):
            return Status.FAILURE

        response = await self.handler.handle_action(data["action_type"], data)
        if not response:
            return Status.FAILURE
        # TODO: I think the message uuid handling should be done in the stream level
        return self.send_message(sock, response, data["message_uuid"])

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
    def get_content(self):
        pass
