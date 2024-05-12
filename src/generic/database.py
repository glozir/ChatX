import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dataclasses import dataclass
from functools import wraps

from src.generic.types import * 


def find_by_attribute(collection_name: str, attribute: str, class_type):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, value):
            collection = getattr(self.db, collection_name)
            obj = await collection.find_one({attribute: value})
            if obj:
                return class_type(**obj)
            return None
        return wrapper
    return decorator

def insert_into_collection(collection_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, obj):
            collection = getattr(self.db, collection_name)
            await collection.insert_one(obj.__dict__)
        return wrapper
    return decorator

class AsyncMongoDBClient:
    def __init__(self, uri='mongodb://localhost:27017/', db_name='x_database'):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    @insert_into_collection("users")
    async def add_user(self, user: Dataclass.User):
        pass

    @insert_into_collection("sessions")
    async def add_session(self, session: Dataclass.Session):
        pass

    @find_by_attribute("users", "name", Dataclass.User)
    async def find_user_by_name(self, name):
        pass

    @find_by_attribute("threads", "uuid", Dataclass.Session)
    async def find_session_by_uuid(self, uuid):
        pass

    # @find_by_attribute("threads", "uuid", Dataclass.Thread)
    async def find_thread_by_parent_and_uuid(self, parent, uuid):
        pass

