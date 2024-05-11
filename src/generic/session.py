from src.generic.types import * 
from datetime import datetime 

class Session(): 
    def __init__(self, uuid, content=None, content_type=None, user=None, upload_time=None, num_of_threads=None):   
        self.uuid = uuid 
        self.threads = []
        self.content : bytes = content
        self.content_type : ContentType = content_type 
        self.user : str = user 
        self.upload_time : datetime = upload_time 
        self.num_of_threads : int = num_of_threads

    def append(self, thread):
        self.threads.append(thread)
    
    def create_thread(self, **content): 
        self.append(Thread(self, , **content))

    def get_content(self): 
        return self.content, self.content_type, self.user, self.upload_time, self.num_of_threads

    def get_threads(self): 
        return self.threads
    
class Thread(Session):
    def __init__(self, parent, uuid, **content):
        super().__init__(content)
        
        self.parent = parent