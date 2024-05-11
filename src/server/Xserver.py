from src.generic.types import *
from src.generic.server.stream import StreamServer
from src.server.action_handler import Xhandler
from src.generic.session import Thread, Session
from src.generic.database import AsyncMongoDBClient
from src.generic.utils import create_uuid 
from bcrypt import hashpw, gensalt, checkpw

class Xserver(StreamServer): 
    def __init__(self, db_url, **kwargs) -> None:
        super().__init__(**kwargs)   
        
        self.database_handler = AsyncMongoDBClient()
        self.handler = Xhandler 
        self.users = {} # key : username
        self.sessions : Session = {} # uuid : session 

    async def recv_action(self, sock):
        return await self.handle_action(super().recv_action(sock)) 

    async def handle_action(self, sock, data): 
        if not data.get("action_type"):
            return Status.FAILURE
        
        response = await self.handler.handle_action(data["action_type"], data)
        if not response: 
            return Status.FAILURE
        return self.send_message(sock, response, data["message_uuid"])

    def assign_key(self, username): 
        key = create_uuid() # FIXME: change this logic 
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
        
        await self.database_handler.add_user(GenericDataclass.User(username, hashpw(password, gensalt())))
        return self.assign_key(username)

    @Xhandler(ActionType.CreateSession)
    async def create_session(self): 
        pass

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
    







