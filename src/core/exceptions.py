from http import HTTPStatus
from typing import Optional


class CustomException(Exception):
    """
    Base Exception for Custom Exceptions/Errors
    NOTE: NOT raised anywhere! (it's a base class for other custom exceptions)
    """

    status: HTTPStatus

    def __init__(self, message: Optional[str] = None):
        if message:
            self.message = message


class BadRequestException(CustomException):
    """ custom exception for malformed and unprocessable requests """
    status = HTTPStatus.BAD_REQUEST


class UnauthenticatedException(CustomException):
    """ custom exception for forbidden operations for unauthenticated users """

    status = HTTPStatus.UNAUTHORIZED  # 401


class ForbiddenException(CustomException):
    """
    custom exception for inaccessible operations for users (authenticated,
    but doesn't have access to an endpoint or a special operation)
    """

    status = HTTPStatus.FORBIDDEN  # 403


class NotFoundException(CustomException):
    """ custom exception for non-existent and non-accessible objects """

    status = HTTPStatus.NOT_FOUND  # 404


class DuplicateValueException(CustomException):
    """
    custom exception for unique fields when a user enters a duplicate input
    while creating or updating an object (e.g. an existing `username`, etc.)
    """

    status = HTTPStatus.UNPROCESSABLE_ENTITY  # 422

    def __init__(self, field: str, message: Optional[str] = None):
        self.field = field
        super().__init__(message)


class InternalServerError(CustomException):
    """ custom exception for unpredicted server errors and problems """

    status = HTTPStatus.INTERNAL_SERVER_ERROR  # 500
