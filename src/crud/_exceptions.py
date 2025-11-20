""" crud-specific custom exceptions/errors """

from http import HTTPStatus
from typing import Optional

from src.core.exceptions import CustomException


class DuplicateValueException(CustomException):
    """ ... """

    status = HTTPStatus.UNPROCESSABLE_ENTITY  # 422

    def __init__(self, field: str, message: Optional[str] = None):
        self.field = field
        super().__init__(message)
