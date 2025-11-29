from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.core.exceptions import InternalServerError


async def handle_unexpected_db_error(
    db: AsyncSession, failed_operation: str, err: SQLAlchemyError
):
    await db.rollback()
    msg = f"Failed to {failed_operation}! unexpected database error."
    # ToDo: here needs to be `logged` properly
    raise InternalServerError(msg) from err
