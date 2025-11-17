from http import HTTPStatus
from typing import Optional


class CustomException(Exception):
    """
    Base Exception for Custom Exceptions/Errors

    used as BaseClass:
        in this module (right here):
            UnauthorizedException
            ForbiddenException
            InternalServerError
        in crud/_exceptions.py:
            DuplicateValueException

    NOT raised anywhere...! (it's a base class for other custom exceptions)
    """

    status: HTTPStatus

    def __init__(self, message: Optional[str] = None):
        if message:
            self.message = message


class BadRequestException(CustomException):
    """ ... """
    status = HTTPStatus.BAD_REQUEST


class UnauthorizedException(CustomException):
    """
    used as BaseClass:
        auth/_exceptions.py:
            JWTDecodeError
            TokenError

    raised in:
        ...
    """

    status = HTTPStatus.UNAUTHORIZED  # 401


class ForbiddenException(CustomException):
    """ ... """

    status = HTTPStatus.FORBIDDEN  # 403


class NotFoundException(CustomException):
    """ ... """

    status = HTTPStatus.NOT_FOUND  # 404


class InternalServerError(CustomException):
    """
    custom exception for unpredicted server errors and problems

    raised in:
        ...
    """

    status = HTTPStatus.INTERNAL_SERVER_ERROR  # 500
