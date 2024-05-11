from src.generic.types import * 
from src.generic.utils import create_uuid 
from datetime import datetime 

class Session(): 
    def __init__(self, uuid, content : Content = None):   
        self.uuid = uuid 
        self.threads = []
        self.content : Content = content

    def append(self, thread):
        self.threads.append(thread)
    
    def create_thread(self, Content): 
        self.append(Thread(self, create_uuid(), Content))

    def get_content(self): 
        return self.content

    def get_threads(self): 
        return self.threads
    
class Thread(Session):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs) 
        
        self.parent = parent