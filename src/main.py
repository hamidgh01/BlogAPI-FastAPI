from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.redis import init_redis, close_redis


@asynccontextmanager
async def lifespan(application: FastAPI):
    redis_ = await init_redis()
    application.state.redis = redis_  # is used as a dependency
    yield
    await close_redis(redis_)


app = FastAPI(
    title="Blog API - FastAPI",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"syntaxHighlight.theme": "monokai"}
)


@app.get("/")
async def home(db: Annotated[AsyncSession, Depends(get_db)]):
    return "Hello world!"


# app.include_router(...)
