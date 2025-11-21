"""
security utils:
    - JWTBearer
    - PasswordHandler

(each one explained in its docstring)
"""

from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from .exceptions import UnauthorizedException


class JWTBearer(HTTPBearer):
    """
    Override HTTPBearer:
    -> raise HTTP_401_UNAUTHORIZED instead of HTTP_403_FORBIDDEN
    """

    def __init__(self, **kwargs):
        super().__init__(auto_error=False, **kwargs)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials = await super().__call__(request)
        # WHETHER : if not (authorization and scheme and credentials):
        # OR      : if credentials.scheme.lower() != "bearer":
        #           ---> credentials will be 'None' due to "auto_error=False"
        if credentials is None:
            raise UnauthorizedException(
                "Authentication failed: Invalid Credentials."
            )
        return credentials


class PasswordHandler:
    """
    enables saving hashed-passwords in database instead of plain-passwords

    methods:
    - hash_password() :
        takes plain-password and returns its hashed-value
    - verify_password() :
        takes a plain-password and a hashed-password and checks
        whether the password verifies against the hash
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def hash_password(password: str) -> str:
        return PasswordHandler.pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return PasswordHandler.pwd_context.verify(
            plain_password,
            hashed_password
        )


jwt_bearer = JWTBearer()  # Customized HTTPBearer
