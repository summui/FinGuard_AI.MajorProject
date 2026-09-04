# MongoDB client setup and Beanie ODM initialization handlers
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.expense import Expense

async def init_db():
    client = AsyncIOMotorClient(settings.mongo_uri)
    await init_beanie(
        database=client[settings.mongo_db_name],
        document_models=[User, Expense],
    )