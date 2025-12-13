from fastapi import APIRouter, Depends

from src.utils import dependencies as deps


admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(deps.authenticate_admin)]
)
