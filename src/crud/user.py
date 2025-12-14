from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy import select, delete, or_, and_, desc
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError, MultipleResultsFound

from src.models import User, follows
from src.core.security import PasswordHandler
from src.core.exceptions import (
    InternalServerError,
    NotFoundException,
    BadRequestException,
    DuplicateValueException
)

from .utils import handle_unexpected_db_error

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from pydantic import EmailStr

    from src.schemas.user import (
        UserCreate,
        UserUpdate,
        SetPassword,
        UserLoginRequest,
        FollowCreate,
        UnfollowOrRemoveFollowerSchema
    )


class UserCrud:
    """ CRUD operations for User model """

    @staticmethod
    @handle_unexpected_db_error("create user")
    async def create(data: UserCreate, db: AsyncSession) -> User:
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

    @staticmethod
    @handle_unexpected_db_error("update user")
    async def update(user: User, data: UserUpdate, db: AsyncSession) -> User:
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

    @staticmethod
    @handle_unexpected_db_error("set new password")
    async def set_new_password(
        user: User, data: SetPassword, db: AsyncSession
    ) -> None:
        new_password_hash = PasswordHandler.hash_password(data.password)
        user.password = new_password_hash
        await db.commit()

    @staticmethod
    @handle_unexpected_db_error("verify user for login")
    async def verify_user_for_login(
        data: UserLoginRequest, db: AsyncSession
    ) -> User | None:
        query = select(User).where(or_(
            User.username == data.identifier, User.email == data.identifier
        ))  # NOTE: data.identifier is whether `username` or `email`
        result = await db.execute(query)
        user: Optional[User] = result.scalar_one_or_none()
        if user is None:
            return

        is_password_verified = PasswordHandler.verify_password(
            plain_password=data.password, hashed_password=user.password
        )
        if not is_password_verified:
            return

        return user

    @staticmethod
    @handle_unexpected_db_error("delete user")
    async def delete(user: User, db: AsyncSession) -> None:
        await db.delete(user)
        await db.commit()

    @staticmethod
    @handle_unexpected_db_error("get user by 'id'")
    async def get_by_id(pk: int, db: AsyncSession) -> User:  # ToDo: change it to: [id, username]
        user = await db.get(User, pk)
        if user is None:
            raise NotFoundException(f"User with 'ID={pk}' is not found!")
        return user

    @staticmethod
    @handle_unexpected_db_error("get user by 'username'")
    async def get_by_username(username: str, db: AsyncSession) -> User:
        return await UserCrud._get_user_by_unique_field("username", username, db)

    @staticmethod
    @handle_unexpected_db_error("get user by 'email'")
    async def get_by_email(email: EmailStr, db: AsyncSession) -> User:
        return await UserCrud._get_user_by_unique_field("email", email, db)

    @staticmethod
    async def retrieve_list(db: AsyncSession) -> list[User]:
        # query = select(User.ID, User.username).where(...)
        # users = await db.execute(query)...
        # ...
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


class FollowCrud:
    """ CRUD operations for 'follows' table """

    @staticmethod
    @handle_unexpected_db_error("add follow relation")
    async def create(
        current_user_id: int, data: FollowCreate, db: AsyncSession
    ) -> Literal[1, 0]:
        """ a user `follows` another one """
        query = pg_insert(follows).values(
            followed_by=current_user_id, followed=data.intended_user_id
        ).on_conflict_do_nothing(index_elements=["followed_by", "followed"])
        try:
            result = await db.execute(query)
            await db.commit()
            return result.rowcount  # Literal[1, 0]
        except IntegrityError as e:
            if 'foreign key constraint "follows_followed_fkey"' in str(e.orig):
                raise BadRequestException(
                    f"there's no user with pk={data.intended_user_id}."
                )

    @staticmethod
    @handle_unexpected_db_error("delete follow relation")
    async def delete(
        current_user_id: int,
        data: UnfollowOrRemoveFollowerSchema,
        db: AsyncSession
    ) -> Literal[1, 0]:
        """ a user `unfollows` another one, or `removes` a follower """
        match data.operation_type:
            case "unfollow":
                and_clause = and_(
                    follows.c.followed_by == current_user_id,
                    follows.c.followed == data.intended_user_id
                )
            case "remove":
                and_clause = and_(
                    follows.c.followed_by == data.intended_user_id,
                    follows.c.followed == current_user_id
                )
            case _:
                raise BadRequestException("invalid operation-type input!")
        query = delete(follows).where(and_clause)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount  # Literal[1, 0]

    @staticmethod
    @handle_unexpected_db_error("get followers-list")
    async def retrieve_followers(
        user_id: int, db: AsyncSession
    ) -> list[tuple[int, str]]:  # [(id, username), (id, username), ...]
        query = (
            select(follows.c.followed_by, User.username)
            .join(User, follows.c.followed_by == User.ID)
            .where(follows.c.followed == user_id)
            .order_by(desc(follows.c.follow_at))
        )
        rows = (await db.execute(query)).all()
        await db.commit()
        return rows

    @staticmethod
    @handle_unexpected_db_error("get followings-list")
    async def retrieve_followings(
        user_id: int, db: AsyncSession
    ) -> list[tuple[int, str]]:  # [(id, username), (id, username), ...]
        query = (
            select(follows.c.followed, User.username)
            .join(User, follows.c.followed == User.ID)
            .where(follows.c.followed_by == user_id)
            .order_by(desc(follows.c.follow_at))
        )
        rows = (await db.execute(query)).all()
        await db.commit()
        return rows
