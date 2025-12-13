""" post-related routes | gets service from PostService """

from typing import Annotated

from fastapi import APIRouter, status, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
# from redis.asyncio import Redis

from src.utils import dependencies as deps
from src.schemas import post as post_sch
from src.schemas.GENERAL import Message
from src.services import PostService


router = APIRouter(prefix="/posts")


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_draft_post(
    current_user_id: Annotated[int, Depends(deps.get_current_user_id)],
    data: post_sch.PostCreate,
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> dict:
    draft, tags = await PostService.add_draft_post(current_user_id, data, db)
    return {"draft_post": draft, "tags": tags}


@router.put("/publish/{pk}", status_code=status.HTTP_202_ACCEPTED)
async def publish(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of post")],
    current_user_id: Annotated[int, Depends(deps.get_current_user_id)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> post_sch.PostDetailsOut:
    return await PostService.publish(current_user_id, pk, db)


@router.put("/{pk}", status_code=status.HTTP_202_ACCEPTED)
async def update_post(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of post")],
    current_user_id: Annotated[int, Depends(deps.get_current_user_id)],
    data: post_sch.PostUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> post_sch.PostOut:
    return await PostService.update_post_fields(current_user_id, pk, data, db)


@router.put("/tags/{pk}", status_code=status.HTTP_202_ACCEPTED)
async def update_post_tags(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of post")],
    current_user_id: Annotated[int, Depends(deps.get_current_user_id)],
    data: post_sch.TagsIn,
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> list[post_sch.TagOut]:
    return await PostService.update_tags_of_post(current_user_id, pk, data, db)


@router.patch("/privacy/{pk}", status_code=status.HTTP_202_ACCEPTED)
async def change_privacy_statement(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of post")],
    current_user_id: Annotated[int, Depends(deps.get_current_user_id)],
    data: post_sch.ChangePostPrivacy,
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Message:
    res = await PostService.change_privacy_stmt(current_user_id, pk, data, db)
    return Message(message=f"post's privacy successfully changed to: {res}")


@router.delete("/{pk}", status_code=status.HTTP_202_ACCEPTED)
async def delete_post_at_user_request(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of post")],
    current_user_id: Annotated[int, Depends(deps.get_current_user_id)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Message:
    await PostService.delete_post_at_user_request(current_user_id, pk, db)
    return Message(message="post deleted successfully.")
