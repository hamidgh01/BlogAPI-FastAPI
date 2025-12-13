from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.redis import init_redis, close_redis
from src.core.exceptions import CustomException
from src.utils.exception_handlers import custom_exception_handler
from src.routes import user, post
from src.routes.admin import admin_router


all_routers = [user.router, post.router, admin_router]


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

app.add_exception_handler(CustomException, custom_exception_handler)


@app.get("/")
async def home():
    return "Welcome to this Blog!"


for router in all_routers:
    app.include_router(router)
