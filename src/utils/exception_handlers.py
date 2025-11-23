from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import CustomException


async def custom_exception_handler(
    request: Request, err: CustomException
):
    return JSONResponse(
        content={"message": err.message},
        status_code=err.status.value
    )
