""" basic settings of the database """

from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)

from .config import settings


engine = create_async_engine(
    url=str(settings.SQLALCHEMY_DB_URL),
    echo=True,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)
