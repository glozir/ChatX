from src.generic.types import *
from src.generic.server.stream import StreamServer
from src.server.action_handler import Xhandler
from src.generic.session import Thread, Session

class Xserver(StreamServer): 
    def __init__(self, address) -> None:
        super().__init__(address)   
        
        self.handler = Xhandler 
        self.users = {} # key : username
        self.sessions : Session = {} # uuid : session 

    def recv_action(self, sock):
        return self.handle_action(super().recv_action(sock)) 

    def handle_action(self, sock, data): 
        if not data.get("action_type"):
            return Status.FAILURE
        
        response = self.handler.handle_action(data["action_type"], data)
        if not response: 
            return Status.FAILURE
        return self.send_message(sock, response)


    @Xhandler(ActionType.Authenticate)
    def authenticate(self, username, password): 
        pass

    @Xhandler(ActionType.CreateUser)
    def create_user(self, username, password):
        pass

    @Xhandler(ActionType.CreateSession)
    def create_session(self): 
        pass

    @Xhandler(ActionType.CreateThread)
    def create_thread(self):
        pass

    @Xhandler(ActionType.GetSessions)
    def get_sessions(self):
        pass

    @Xhandler(ActionType.GetThreads)
    def get_threads(self):
        pass

    @Xhandler(ActionType.GetContent)
    def get_content(self): 
        pass
    







