""" auth-specific custom exceptions/errors """

from typing import Optional

from src.core.exceptions import UnauthorizedException


class JWTDecodeError(UnauthorizedException):
    """custom exception for invalid tokens -> unable to be decoded correctly"""

    def __init__(self, message: Optional[str] = None):
        message = f"Authentication failed: {message}" if message else None
        super().__init__(message)


class TokenError(UnauthorizedException):
    """
    custom exception for invalid decoded-tokens (expired, revoked, wrong-type)
    """

    def __init__(self, message: Optional[str] = None):
        message = f"Authentication failed: {message}" if message else None
        super().__init__(message)
