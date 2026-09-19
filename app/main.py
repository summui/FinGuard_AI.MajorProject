import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.routers import auth, finance, contracts, advisor
from app.models.user import User
from app.models.expense import Expense
from app.models.contract import Contract


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.mongo_uri)
    database = client[settings.mongo_db_name]

    await init_beanie(database=database, document_models=[User, Expense, Contract])

    yield

    client.close()


app = FastAPI(
    title="FinGuard AI",
    description="Personal Finance & Contract Risk Analysis Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(finance.router)
app.include_router(contracts.router)
app.include_router(advisor.router)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")