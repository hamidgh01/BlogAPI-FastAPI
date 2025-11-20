from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy import select, or_
from sqlalchemy.exc import (
    IntegrityError, MultipleResultsFound, SQLAlchemyError
)

from src.models import User
from src.core.security import PasswordHandler
from src.core.exceptions import (
    InternalServerError,
    NotFoundException,
    BadRequestException,
    UnauthorizedException
)
from ._exceptions import DuplicateValueException

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from pydantic import EmailStr

    from src.schemas.user import (
        CreateUserSchema,
        UpdateUserSchema,
        SetPasswordSchema,
        UserLoginSchema,
    )


class UserCrud:
    """ CRUD operations for User model """

    @staticmethod
    async def create(data: CreateUserSchema, db: AsyncSession) -> User:
        try:
            data = data.model_dump(exclude={"confirm_password"})
            data["password"] = PasswordHandler.hash_password(data["password"])
            user = User(**data)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user

        except IntegrityError as err:
            await db.rollback()
            to_raise = UserCrud._handle_unique_constraint_exceptions(err, data)
            if to_raise is not None:
                raise to_raise from err

            # ToDo: here needs to be `logged` properly
            msg = "Failed to create `User`! unexpected integrity error."
            raise InternalServerError(msg) from err

        except SQLAlchemyError as err:
            await db.rollback()
            # ToDo: here needs to be `logged` properly
            msg = "Failed to create `User`! unexpected database error."
            raise InternalServerError(msg) from err

    @staticmethod
    async def update(
        user: User, data: UpdateUserSchema, db: AsyncSession
    ) -> User:
        data = data.model_dump(exclude_none=True)
        if not data:
            raise BadRequestException("Empty field values to update.")
        try:
            for k, v in data.items():
                setattr(user, k, v)  # 'None' values excluded before
            await db.commit()
            await db.refresh(user)
            return user

        except IntegrityError as err:
            await db.rollback()
            to_raise = UserCrud._handle_unique_constraint_exceptions(err, data)
            if to_raise is not None:
                raise to_raise from err

            # ToDo: here needs to be `logged` properly
            msg = "Failed to update `User`! unexpected integrity error."
            raise InternalServerError(msg) from err

        except SQLAlchemyError as err:
            await db.rollback()
            # ToDo: here needs to be `logged` properly
            msg = "Failed to update `User`! Unexpected database error."
            raise InternalServerError(msg) from err

    @staticmethod
    async def set_new_password(
        user: User, data: SetPasswordSchema, db: AsyncSession
    ) -> None:
        try:
            new_password_hash = PasswordHandler.hash_password(data.password)
            user.password = new_password_hash
            await db.commit()
        except SQLAlchemyError as err:
            await db.rollback()
            msg = "Failed to set new password! Unexpected database error."
            raise InternalServerError(msg) from err

    @staticmethod
    async def verify_password(data: UserLoginSchema, db: AsyncSession) -> User:
        query = select(User).where(or_(
            User.username == data.identifier, User.email == data.identifier
        ))  # NOTE: data.identifier is whether `username` or `email`
        result = await db.execute(query)
        user: Optional[User] = result.scalars().one_or_none()

        if user is None:
            raise UnauthorizedException("Invalid username, email or password")

        is_password_verified = PasswordHandler.verify_password(
            plain_password=data.password, hashed_password=user.password
        )
        if not is_password_verified:
            raise UnauthorizedException("Invalid username, email or password")

        return user

    @staticmethod
    async def delete(user: User, db: AsyncSession) -> None:
        try:
            await db.delete(user)
            await db.commit()
        except SQLAlchemyError as err:
            await db.rollback()
            # ToDo: here needs to be `logged` properly
            msg = "Failed to delete `User`! Unexpected database error."
            raise InternalServerError(msg) from err

    @staticmethod
    async def get_by_id(pk: int, db: AsyncSession) -> User:
        user = await db.get(User, pk)
        if user is None:
            raise NotFoundException(f"User with 'ID={pk}' is not found!")
        return user

    @staticmethod
    async def get_by_username(username: str, db: AsyncSession) -> User:
        return await UserCrud._get_user_by_unique_field("username", username, db)

    @staticmethod
    async def get_by_email(email: EmailStr, db: AsyncSession) -> User:
        return await UserCrud._get_user_by_unique_field("email", email, db)

    @staticmethod
    async def retrieve_list(db: AsyncSession) -> list[User]:
        # query = select(User.ID, User.username).where(...)
        # users = await db.execute(query)...
        # ...
        pass  # ToDo: implement later

    # READ from 'follows' association table
    @staticmethod
    async def retrieve_followers(db: AsyncSession) -> list[User]:
        pass  # ToDo: implement later

    # READ from 'follows' association table
    @staticmethod
    async def retrieve_followings(db: AsyncSession) -> list[User]:
        pass  # ToDo: implement later

    # ----------------------------------------------------------------
    # private methods:

    @staticmethod
    def _handle_unique_constraint_exceptions(
        err: IntegrityError, data: dict
    ) -> DuplicateValueException | None:
        """
        takes an `err: IntegrityError` -> breaks it down and check if
        the error's reason is due to unique-constraints or not:
        - if yes : return a proper custom-exception and message
        - if no  : return None
        """
        if "ix_users_username" in str(err.orig):
            return DuplicateValueException(
                field="username",
                message=f"The username {data.get("username")!r} is taken "
                        f"before! Please choose another one."
            )
        if "users_email_key" in str(err.orig):
            return DuplicateValueException(
                field="email",
                message=f"The email address {data.get("email")!r} is used "
                        f"before. Please enter another email address."
            )
        return None

    @staticmethod
    async def _get_user_by_unique_field(
        field_name: Literal["username", "email"], value, db: AsyncSession
    ) -> User:
        if field_name == "username":
            query = select(User).where(User.username == value)
            # maybe change to: select(User.ID, User.username).where(...)
        elif field_name == "email":
            query = select(User).where(User.email == value)

        try:
            user = (await db.execute(query)).scalars().one_or_none()
            if user is None:
                raise NotFoundException(
                    f"User with {field_name}={value!r} is not found!"
                )
        except MultipleResultsFound as err:
            msg = f"Multiple users with {field_name}={value!r} is found!"
            # ToDo: here needs to be `logged` properly
            raise InternalServerError(msg) from err

        return user
