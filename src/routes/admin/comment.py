from typing import Annotated
from fastapi import status, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils import dependencies as deps
from src.schemas.GENERAL import Message
from src.services import CommentService

from ._admin_router import admin_router


@admin_router.patch(
    "/comments/hide/{pk}", status_code=status.HTTP_202_ACCEPTED
)
async def hide_comment(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of comment")],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Message:
    await CommentService.hide_comment(pk, db)
    return Message(message="comment hid successfully.")


@admin_router.patch(
    "/comments/unhide/{pk}", status_code=status.HTTP_202_ACCEPTED
)
async def unhide_comment(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of comment")],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Message:
    await CommentService.unhide_comment(pk, db)
    return Message(message="comment un-hid (republished) successfully.")


@admin_router.delete("/comments/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of comment")],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    await CommentService.delete_comment(pk, db)
