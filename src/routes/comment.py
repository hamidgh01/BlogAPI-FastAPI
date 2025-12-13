""" comment-related routes | gets service from CommentService """

from typing import Annotated

from fastapi import APIRouter, status, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils import dependencies as deps
from src.schemas import comment as comment_sch
from src.schemas.GENERAL import Message
from src.services import CommentService as CMService


router = APIRouter(prefix="/comments")


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_comment(
    current_user_id: Annotated[int, Depends(deps.get_current_user_id)],
    data: comment_sch.CommentCreate,
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> comment_sch.CommentOut:
    return await CMService.add_comment(current_user_id, data, db)


@router.put("/{pk}", status_code=status.HTTP_202_ACCEPTED)
async def update_comment(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of comment")],
    current_user_id: Annotated[int, Depends(deps.get_current_user_id)],
    data: comment_sch.CommentUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> comment_sch.CommentOut:
    return await CMService.update_comment(current_user_id, pk, data, db)


@router.delete("/{pk}", status_code=status.HTTP_202_ACCEPTED)
async def delete_comment_at_user_request(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of comment")],
    current_user_id: Annotated[int, Depends(deps.get_current_user_id)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Message:
    await CMService.delete_comment_at_user_request(current_user_id, pk, db)
    return Message(message="comment deleted successfully.")
