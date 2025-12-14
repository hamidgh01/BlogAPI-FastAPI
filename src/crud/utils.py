from functools import wraps
from typing import Callable, Awaitable, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.core.exceptions import InternalServerError


def handle_unexpected_db_error(operation_name: str):

    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except SQLAlchemyError as err:
                db: AsyncSession | None = kwargs.get("db")
                if db is None:
                    for arg in args:
                        if isinstance(arg, AsyncSession):
                            db = arg
                            break
                    else:
                        raise RuntimeError(
                            "db (AsyncSession) not found in function arguments"
                        ) from err

                await db.rollback()
                # TODO: proper logging here
                raise InternalServerError(
                    f"Failed to {operation_name}! unexpected database error."
                ) from err

        return wrapper

    return decorator
