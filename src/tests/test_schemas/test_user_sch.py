from datetime import datetime, timedelta

import pytest

from src.schemas import (
    CreateUserSchema,
    UpdateUserSchema,
    UpdateUserForAdminSchema,
    UpdatePasswordSchema,
    # SetNewPassword,  Doesn't need to be tested
    UserLoginSchema,
    UserOutForClientSchema,
    # UserListForAdminSchema,  Doesn't need to be tested
    UserDetailsForAdminSchema,  # includes all fields in UserListForAdminSchema
    FollowOrUnfollowSchema,
    FollowerOrFollowingListSchema
)
# NOTE: repeated functionalities and validation in different Schemas
# is tested just for one time!


@pytest.mark.parametrize(argnames="invalid_username, expected", argvalues=[
    ("ab", "| length: 3-64"),  # NOTE: expected pattern -> r'[a-z0-9_]{3,64}'
    ("a" * 65, "| length: 3-64"),  # length > 64
    ("Test", "[username] allowed characters: "),
    ("test ", "'a-z', '0-9', '_' "),
    ("test-", "(NO capital letters or spaces) |")
])
def test_invalid_username_patterns(invalid_username, expected):
    valid_fields = {
        "email": "test@email.com",
        "password": "test_password",
        "confirm_password": "test_password"
    }
    with pytest.raises(ValueError) as err:
        CreateUserSchema(username=invalid_username, **valid_fields)
    assert expected in err.value.__str__()


@pytest.mark.parametrize(
    "schema", [CreateUserSchema, UpdateUserForAdminSchema, UpdateUserSchema]
)
def test_create_and_update_user_schemas_behaviour_with_invalid_email(schema):
    """ IMPORTANT NOTE:
    this `test` doesn't test various invalid email formats, because
    it is covered by Pydantic internally (via EmailStr).
    this `test` ensures that CreateUser/UpdateUser/UpdateUserForAdmin Schemas
    behave correctly (reject) with invalid email-address formats.
    """
    fields = {
        "username": "test",
        "email": "invalid@@example..com",  # invalid email format
        "password": "test_password",
        "confirm_password": "test_password"
    }
    with pytest.raises(ValueError) as err:
        schema(**fields)
    assert "value is not a valid email address" in err.value.__str__()


# p: password  / cp: confirm_password
@pytest.mark.parametrize(argnames="p, cp, expected", argvalues=[
    ("short", "short", "|  length: '8 <= password <= 64'"),
    ("abc" * 25, "abc" * 25, "|  length: '8 <= password <= 64'"),
    ("includes space ", "includes space ", "[password] can not include"),
    ("new_line\n", "new_line\n", " whitespace characters (space,"),
    ("includes_tab\t", "includes_tab\t", " newline, etc...)  |")
])
def test_invalid_password_patterns_and_unmatched_passwords(p, cp, expected):
    valid_fields = {"username": "test", "email": "test@example.com"}
    with pytest.raises(ValueError) as err:
        CreateUserSchema(password=p, confirm_password=cp, **valid_fields)
    assert expected in err.value.__str__()


def test_healthiness_of_create_user_schema():
    """
    test successful validation and serialization in "CreateUserSchema()" with
    valid 'username' & 'email' & 'password' patterns + matched passwords
    """
    fields = {
        "username": "test_uname",
        "email": "test@email.com",
        "password": "test_password",
        "confirm_password": "test_password"
    }
    cre_user_sch = CreateUserSchema(**fields)
    assert cre_user_sch.username == "test_uname"
    assert cre_user_sch.email == "test@email.com"
    assert cre_user_sch.password == "test_password"


def test_healthiness_of_update_user_schema():
    """
    test successful validation and serialization in
    "UpdateUserSchema()" with valid 'username' & 'email'
    """
    upd_user_sch = UpdateUserSchema(username="hamid", email=None)
    assert upd_user_sch.username == "hamid"
    assert upd_user_sch.email is None
    upd_user_sch = UpdateUserSchema(username=None, email="hamid.gh@gmail.com")
    assert upd_user_sch.username is None
    assert upd_user_sch.email == "hamid.gh@gmail.com"


def test_healthiness_of_update_user_for_admin_schema():
    """
    test successful validation and serialization in
    "UpdateUserForAdminSchema()" with valid 'username' & 'email' &
    'is_active' & 'is_superuser' values
    """
    # 'username' and 'email' are tested in previous test
    upd_user_sch = UpdateUserForAdminSchema(
        username="hamid", email="a@a.com", is_active=False, is_superuser=None
    )
    assert upd_user_sch.is_active is False
    assert upd_user_sch.is_superuser is None
    upd_user_sch = UpdateUserForAdminSchema(
        username="hamid", email=None, is_active=None, is_superuser=True
    )
    assert upd_user_sch.is_active is None
    assert upd_user_sch.is_superuser is True


def test_healthiness_of_update_password_schema():
    """
    test successful validation and serialization in "UpdatePasswordSchema()"
    with valid 'password' patterns and matched passwords
    """
    user_pass_schema = UpdatePasswordSchema(
        password="abcde12345",
        confirm_password="abcde12345",
        old_password="12345678"
    )
    assert user_pass_schema.password == "abcde12345"


def test_healthiness_of_user_login_schema():
    """ test successful validation and serialization in UserLoginSchema() """

    sch1 = UserLoginSchema(identifier="hamid01", password="7686453452")
    sch2 = UserLoginSchema(identifier="hamid@example.com", password="test1234")
    assert type(sch1.password) is str
    assert sch1.identifier == "hamid01"
    assert sch2.identifier == "hamid@example.com"


def test_healthiness_of_user_out_for_client_schema():
    """ test successful validation and serialization
    in UserOutForClientSchema() """

    sch = UserOutForClientSchema(id=12345, username="hamid01")
    assert type(sch.id) is int and sch.id == 12345
    assert sch.username == "hamid01"


def test_healthiness_of_user_details_for_admin_schema():
    """
    test successful validation and serialization in UserDetailsForAdminSchema()
    """
    sch = UserDetailsForAdminSchema(
        id=543,
        username="test",
        is_active=True,
        is_superuser=False,
        email="test@example.com",
        created_at=datetime.now() - timedelta(days=30),
        updated_at=datetime.now() - timedelta(days=2),
    )
    assert sch.id == 543 and sch.username == "test"
    assert type(sch.is_active) is bool
    assert sch.is_superuser is False
    assert sch.email == "test@example.com"
    assert isinstance(sch.created_at, datetime) is True
    assert sch.updated_at > sch.created_at


def test_healthiness_of_follow_or_unfollow_schema():
    """
    test successful validation and serialization in FollowOrUnfollowSchema()
    """
    sch = FollowOrUnfollowSchema(intended_user_id=2345)
    assert type(sch.intended_user_id) is int and sch.intended_user_id == 2345


def test_healthiness_of_follower_or_following_list_schema():
    """ test successful validation and serialization
    in FollowerOrFollowingListSchema() """

    u_out_sch_1 = UserOutForClientSchema(id=12345, username="hamid01")
    u_out_sch_2 = UserOutForClientSchema(id=1655, username="nobody")

    sch1 = FollowerOrFollowingListSchema()
    sch2 = FollowerOrFollowingListSchema(users_list=[u_out_sch_1])
    sch3 = FollowerOrFollowingListSchema(users_list=[u_out_sch_1, u_out_sch_2])
    assert sch1.users_list is None
    assert sch2.users_list is not None
    assert sch2.users_list[0].username == "hamid01"
    assert len(sch3.users_list) > 1
    assert sch3.users_list[1].id == 1655
    assert sch3.users_list[1].username == "nobody"
