import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dataclasses import dataclass

from src.generic.types import * 

class AsyncMongoDBClient:
    def __init__(self, uri='mongodb://localhost:27017/', db_name='x_database'):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    async def add_user(self, user : GenericDataclass.User):
        await self.db.users.insert_one(user.__dict__)

    async def find_user_by_name(self, username):
        user = await self.db.users.find_one({"name": username})
        if user:
            return GenericDataclass.User(**user)
        return None

