from functools import wraps
from motor.motor_asyncio import AsyncIOMotorClient

from src.generic.session import Session, Thread
from src.generic.types import Dataclass


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
    async def add_session(self, session: Session):
        pass

    async def update_thread(self, thread: Thread):
        pipeline = [
            {
                "$graphLookup": {
                    "from": "sessions",
                    "startWith": "$content.threads",
                    "connectFromField": "content.threads",
                    "connectToField": "uuid",
                    "as": "matched_threads",
                }
            },
            {
                "$match": {
                    "uuid": "thread.parent.uuid"  # Match the thread by its UUID
                }
            },
            {
                "$set": thread.__dict__  # Update the thread with the new data
            },
            {
                "$merge": {
                    "into": "threads",  # Merge the updated document back into the "threads" collection
                    "on": "_id",  # Match documents by their _id field
                    "whenMatched": "replace"  # Replace existing documents with the updated ones
                }
            },
            {
                "$limit": 1
            }
        ]

        await self.db.threads.aggregate(pipeline)

    @find_by_attribute("users", "name", Dataclass.User)
    async def find_user_by_name(self, name):
        pass

    @find_by_attribute("threads", "uuid", Session)
    async def find_session_by_uuid(self, uuid):
        pass

    async def find_thread_by_uuid(self, uuid):
        pipeline = [
            {
                "$graphLookup": {
                    "from": "sessions",
                    "startWith": "$content.threads",
                    "connectFromField": "content.threads",
                    "connectToField": "uuid",
                    "as": "matched_threads",
                    "restrictSearchWithMatch": {"content.threads.uuid": uuid}
                }
            },
            {
                "$project": {
                    "matched_thread": {
                        "$arrayElemAt": ["$matched_threads", 0]
                    }
                }
            },
            {
                "$limit":  1
            }
        ]

        cursor = self.db.sessions.aggregate(pipeline)
        async for session in cursor:
            matched_thread = session.get('matched_thread')
            if matched_thread:
                return Dataclass.Thread(**matched_thread)
        return None
