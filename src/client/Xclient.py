from src.generic.types import * 
from src.generic.client.stream import SecureStream, StreamAuthorized
from src.generic.session import Session, Thread
from src.generic.utils import create_uuid

class Xclient(SecureStream):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
        self.username = None
        self.handler = None

    def authenticate(self, username, password):
        key = self.send_action(ActionType.Authenticate, {
            "password" : password, 
            "username" : username 
        })
        if not key: 
            return Status.FAILURE
        
        self.username = username
        self.handler = SessionHandler(self.address, key) 
        return Status.SUCCESS

    def create_user(self, username, password): 
        response = self.send_action(ActionType.CreateUser, {
            "password" : password, 
            "username" : username 
        }) 
        if not response.get("key"): 
            return Status.FAILURE
        
        self.username = username
        self.handler = SessionHandler(self.address, response.get("key")) 
        return Status.SUCCESS       
    

class SessionHandler(StreamAuthorized):
    def __init__(self, address : Dataclass.Address, key) -> None:
        super().__init__(address, key)

        self.sessions = []


    def create_session(self, content : Dataclass.Content): 
        response = self.send_action(ActionType.CreateSession, {
            "content" : content
        })

        if not response.get("session_uuid"):
            return Status.FAILURE

        self.append(ClientSession(self, response["session_uuid"], content)) 
        return Status.SUCCESS
    
    def get_sessions(self, number=10): 
        response = self.send_action(ActionType.GetSessions, { 
            'number_of_sessions' : number 
        })

        if not response.get("sessions"): 
            return Status.FAILURE
        
        for session in response["sessions"]: 
            if not session.get("session_uuid"): 
                return Status.FAILURE
            self.append(ClientSession(self, session["session_uuid"]))
    
    def append(self, session): 
        self.sessions.append(session)


class ClientSession(Session): 
    def __init__(self, handler, **kwargs):
        super().__init__(**kwargs)

        self.handler = handler

    def send_action(self, action, **kwargs): 
        self.handler.send_action(action, **kwargs)

    def create_thread(self, content : Dataclass.Content): 
        response = self.send_action(ActionType.CreateThread, {
            "content" : content, 
            "parent_uuid" : self.uuid,
        })

        if not response.get("thread_uuid"): 
            return Status.FAILURE
        
        self.append(ClientThread(self.handler, self, response["thread_uuid"], content))
        return Status.SUCCESS
    
    def get_content(self):
        if not super().get_content(): 
            response = self.send_action(ActionType.GetContent, {
                "content_uuid" : self.uuid
            })
            response = response.get("content")
            if not response: 
                return Status.FAILURE
            
            self.content = Dataclass.Content(**response)

            return super().get_content()
        return super().get_content()
    
    def get_threads(self): 
        response = self.send_action(ActionType.GetThreads, {
            "parent_uuid" : self.uuid, 
        })

        if not response.get("threads"): 
            return Status.NOT_FOUND
        
        for thread in response["threads"]: 
            self.append(ClientThread(self.handler, self, response["thread_uuid"]))
        return super().get_threads()


class ClientThread(Thread, ClientSession):
    def __init__(self, handler, parent, **kwargs):
        super(Thread).__init__(parent, **kwargs)
        super(ClientSession).__init__(handler, **kwargs)

        

if __name__ == "__main__":
    pass




