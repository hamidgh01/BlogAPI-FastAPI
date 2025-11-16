from typing import Optional


class CustomException(Exception):
    """ Base Exception for Custom Exceptions/Errors """

    code: int

    def __init__(self, message: Optional[str] = None):
        if message:
            self.message = message


class InternalServerError(CustomException):
    """
    custom exception for unpredicted server errors and other server problems
    """
    code = 500
