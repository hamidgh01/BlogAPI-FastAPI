""" """

from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI, status, HTTPException,
    Query, Path,  # Form, Body,
    File, UploadFile,
    Depends
)
from fastapi.responses import JSONResponse  # RedirectResponse

from sqlalchemy import select  # update, delete
from sqlalchemy.orm import Session

from users.routes import router as user_routes
from blog.routes import router as blog_routes

# from app1.models import *
# from app2.models import *
from core.database import get_db


@asynccontextmanager
async def lifespan(application: FastAPI):
    
    # before 'yield': before Application Startup
    
    # Create all tables at once (initializing database)
    # Base.metadata.create_all(engine)
    # you typically do not need to call 'Base.metadata.create_all(engine)'
    # if you're using Alembic.
    
    # during 'yield': Application Lifecycle
    yield  # (application runs and handles Http Requests/Responses)
    
    # after 'yield': after Application shutdown


# app = FastAPI(lifespan=lifespan)
app = FastAPI(
    title="My API",
    lifespan=lifespan,
    docs_url="/docs",  # Argument equals to the default parameter value (I disabled the inspection)
    redoc_url="/redoc",  # ...
    openapi_url="/openapi.json",  # ...
    swagger_ui_parameters={"syntaxHighlight.theme": "monokai"}  # forces asset load
)


# @app.get(
#     "/",
#     status_code=status.HTTP_200_OK,
#     response_model=list[...],
# )
# def home/index/root(
#     ...
#     ...
# ):
#     ...
#     ...


#

app.include_router(user_routes)
app.include_router(blog_routes)
