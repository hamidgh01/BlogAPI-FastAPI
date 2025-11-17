"""
security utils:
    - PasswordHandler
"""

from passlib.context import CryptContext


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
