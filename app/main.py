import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Placeholder router imports (commented out until router files have real code)
# from app.routers import auth, finance, contracts, advisor

# Placeholder Beanie document models (commented out until models are defined)
# from app.models.user import User
# from app.models.expense import Expense
# from app.models.contract import Contract


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Motor client and Beanie ODM on startup
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "finguard_ai")
    client = AsyncIOMotorClient(mongo_uri)
    database = client[db_name]

    document_models = []
    # e.g., document_models = [User, Expense, Contract]
    if document_models:
        await init_beanie(database=database, document_models=document_models)

    yield

    client.close()


app = FastAPI(
    title="FinGuard AI",
    description="Personal Finance & Contract Risk Analysis Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Placeholder router includes (commented out until router files have real code)
# app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
# app.include_router(finance.router, prefix="/api/finance", tags=["Finance"])
# app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])
# app.include_router(advisor.router, prefix="/api/advisor", tags=["Advisor"])

# Mount frontend static files at root "/"
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
