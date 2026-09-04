import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.routers import auth
from app.models.user import User
from app.models.expense import Expense


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "finguard_ai")
    client = AsyncIOMotorClient(mongo_uri)
    database = client[db_name]

    await init_beanie(database=database, document_models=[User, Expense])

    yield

    client.close()


app = FastAPI(
    title="FinGuard AI",
    description="Personal Finance & Contract Risk Analysis Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router, tags=["Auth"])

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")