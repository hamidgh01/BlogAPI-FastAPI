from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy import select, delete, or_, and_, desc
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import (
    IntegrityError, MultipleResultsFound, SQLAlchemyError
)

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
        CreateUserSchema,
        UpdateUserSchema,
        SetPasswordSchema,
        UserLoginRequestSchema,
        FollowSchema,
        UnfollowOrRemoveFollowerSchema
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
            await handle_unexpected_db_error(db, "create `User`", err)

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
            await handle_unexpected_db_error(db, "update `User`", err)

    @staticmethod
    async def set_new_password(
        user: User, data: SetPasswordSchema, db: AsyncSession
    ) -> None:
        try:
            new_password_hash = PasswordHandler.hash_password(data.password)
            user.password = new_password_hash
            await db.commit()
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "set new password", err)

    @staticmethod
    async def verify_user_for_login(
        data: UserLoginRequestSchema, db: AsyncSession
    ) -> User | None:
        query = select(User).where(or_(
            User.username == data.identifier, User.email == data.identifier
        ))  # NOTE: data.identifier is whether `username` or `email`
        try:
            result = await db.execute(query)
            user: Optional[User] = result.scalar_one_or_none()
            if user is None:
                return
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "verify user for login", err)

        is_password_verified = PasswordHandler.verify_password(
            plain_password=data.password, hashed_password=user.password
        )
        if not is_password_verified:
            return

        return user

    @staticmethod
    async def delete(user: User, db: AsyncSession) -> None:
        try:
            await db.delete(user)
            await db.commit()
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "delete `User`", err)

    @staticmethod
    async def get_by_id(pk: int, db: AsyncSession) -> User:  # ToDo: change it to: [id, username]
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
    async def create(
        current_user_id: int, data: FollowSchema, db: AsyncSession
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
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "add follow relation", err)

    @staticmethod
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
        try:
            query = delete(follows).where(and_clause)
            result = await db.execute(query)
            await db.commit()
            return result.rowcount  # Literal[1, 0]
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "delete follow relation", err)

    @staticmethod
    async def retrieve_followers(
        user_id: int, db: AsyncSession
    ) -> list[tuple[int, str]]:  # [(id, username), (id, username), ...]
        query = (
            select(follows.c.followed_by, User.username)
            .join(User, follows.c.followed_by == User.ID)
            .where(follows.c.followed == user_id)
            .order_by(desc(follows.c.follow_at))
        )
        try:
            rows = (await db.execute(query)).all()
            await db.commit()
            return rows
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "get followers-list", err)

    @staticmethod
    async def retrieve_followings(
        user_id: int, db: AsyncSession
    ) -> list[tuple[int, str]]:  # [(id, username), (id, username), ...]
        query = (
            select(follows.c.followed, User.username)
            .join(User, follows.c.followed == User.ID)
            .where(follows.c.followed_by == user_id)
            .order_by(desc(follows.c.follow_at))
        )
        try:
            rows = (await db.execute(query)).all()
            await db.commit()
            return rows
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "get followings-list", err)
