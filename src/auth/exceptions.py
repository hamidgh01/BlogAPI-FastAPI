from src.core.exceptions import CustomException


class JWTDecodeError(CustomException):
    """custom exception for invalid tokens -> unable to be decoded correctly"""
    code = 401


class TokenError(CustomException):
    """
    custom exception for invalid decoded-tokens (expired, revoked, wrong-type)
    """
    code = 401
