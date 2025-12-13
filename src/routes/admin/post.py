from typing import Annotated
from fastapi import status, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils import dependencies as deps
from src.schemas.GENERAL import Message
from src.services import PostService

from ._admin_router import admin_router


@admin_router.patch("/posts/reject/{pk}", status_code=status.HTTP_202_ACCEPTED)
async def reject_post(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of post")],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Message:
    await PostService.reject_post(pk, db)
    return Message(message="post rejected successfully.")


@admin_router.patch(
    "/posts/publish-rejected/{pk}",
    status_code=status.HTTP_202_ACCEPTED
)
async def publish_rejected_post(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of post")],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Message:
    await PostService.publish_rejected_post(pk, db)
    return Message(message="rejection removed successfully.")


@admin_router.delete("/posts/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of post")],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    await PostService.delete_post(pk, db)
