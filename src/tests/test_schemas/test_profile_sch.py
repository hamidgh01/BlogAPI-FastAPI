from datetime import datetime, date, timedelta

from pydantic import ValidationError
import pytest

from src.schemas import (
    # CreateLinkSchema,  # Doesn't need to be tested
    UpdateLinkSchema,
    LinkListSchema,  # includes all fields in CreateLinkSchema
    # InitialProfileSchema,
    UpdateProfileSchema,  # includes all fields in InitialProfileSchema
    # ProfileListSchema,
    ProfileDetailsSchema,  # includes all fields in ProfileListSchema
    UserOutSchema
)
from src.schemas.admin import (
    # ProfileListForAdminPanelSchema,  # Doesn't need to be tested
    ProfileDetailsForAdminPanelSchema,
    UserDetailsForAdminSchema
)

# NOTE: there isn't any custom validator in 'Profile' & 'Link' related Schemas,
# so only the healthiness of these Schemas is tested here.


def test_healthiness_of_update_link_schema():
    """ test successful validation and serialization in UpdateLinkSchema() """
    sch1 = UpdateLinkSchema(profile_id=12358)
    sch2 = UpdateLinkSchema(
        title="youtube",
        url="https://somedomain.net/path",
        profile_id=5432
    )
    assert sch1.title is None and sch1.url is None
    assert sch1.profile_id == 12358
    assert sch2.url.encoded_string() == "https://somedomain.net/path"
    assert str(sch2.url) == "https://somedomain.net/path"
    assert sch2.url.host == "somedomain.net"
    assert sch2.url.path == "/path"
    assert sch2.title == "youtube"

    with pytest.raises(ValidationError) as err:
        UpdateLinkSchema(title="abc" * 25, profile_id=9876)
    assert "String should have at most 64 characters" in str(err.value)

    with pytest.raises(ValidationError) as err:
        UpdateLinkSchema(url="invalid url", profile_id=9876)
    assert "Input should be a valid URL" in err.value.__str__()


def test_healthiness_of_link_list_schema():
    """ test successful validation and serialization in LinkListSchema() """
    sch = LinkListSchema(
        ID=8765432134,
        title="youtube",
        url="https://toplevel.example.com/path/to/details",
        profile_id=765
    )
    assert type(sch.ID) is int
    assert sch.title is not None
    assert sch.profile_id == 765
    assert ".example.com/path/to/details" in sch.url.encoded_string()
    assert str(sch.url) == "https://toplevel.example.com/path/to/details"
    assert sch.url.host == "toplevel.example.com"
    assert sch.url.path == "/path/to/details"
    assert sch.url.scheme == "https"


def test_healthiness_of_update_profile_schema():
    """ test successful validation and serialization in UpdateProfileSchema """

    sch1 = UpdateProfileSchema()
    assert sch1.display_name is None
    assert sch1.about is None
    assert sch1.birth_date is None
    assert sch1.gender.name == "NS" and sch1.gender.value == "not-specified"
    sch2 = UpdateProfileSchema(
        display_name="nobody at nowhere",
        about="a long text as bio or about me\n" * 10,
        birth_date=date(year=2001, month=8, day=21),
        gender="other"
    )
    assert sch2.display_name == "nobody at nowhere"
    assert " as bio or about me\na long text as " in sch2.about
    assert sch2.birth_date.strftime("%B") == "August"
    assert sch2.gender.name == "OT" and sch2.gender.value == "other"

    with pytest.raises(ValidationError) as err:
        UpdateProfileSchema(gender="invalid gender")
    assert "'male', 'female', 'other' or 'not-specified'" in str(err.value)


def test_healthiness_of_profile_details_schema():
    """test successful validation and serialization in ProfileDetailsSchema"""

    sch1 = ProfileDetailsSchema(
        user_id=544,
        follower_count=143,
        following_count=24,
        post_count=0,
        gender="female",
        user=UserOutSchema(
            ID=544,
            username="golang_lover"
        ),
        followed_by_viewer=False
    )

    assert sch1.user_id == sch1.user.ID
    assert type(sch1.post_count) is type(sch1.following_count)
    assert sch1.user.username == "golang_lover"
    assert sch1.gender.value == "female" and sch1.gender.name == "FM"
    assert type(sch1.followed_by_viewer) is bool

    sch2 = ProfileDetailsSchema(
        user_id=48,
        display_name="john doe",
        about="a long description ad bio or about.\n" * 4,
        gender="male",
        birth_date=date(year=1988, month=6, day=29),
        links=[
            LinkListSchema(
                ID=8721,
                title="youtube",
                url="https://youtube.com/path/to/my/channel",
                profile_id=48
            ),
            LinkListSchema(
                ID=3467,
                title="github",
                url="https://github.com/hamidgh01",
                profile_id=48
            ),
        ],
        follower_count=76,
        following_count=201,
        post_count=14,
        user=UserOutSchema(
            ID=48,
            username="abcdefgh"
        ),
        followed_by_viewer=False
    )

    assert sch2.user_id == sch2.user.ID
    assert sch2.user.ID == sch2.links[0].profile_id
    assert type(sch2.about) is str
    assert sch2.display_name == "john doe"
    assert sch2.gender.name == "MA" and sch2.gender.value == "male"
    assert sch2.birth_date.strftime("%B") == "June"
    assert sch2.links[0].title == "youtube"
    assert sch2.links[0].url.path == "/path/to/my/channel"
    assert sch2.links[1].title == "github"
    assert sch2.links[1].url.encoded_string() == "https://github.com/hamidgh01"
    assert sch2.user.username == "abcdefgh"


def test_healthiness_of_profile_details_for_admin_panel_schema():
    """ test successful validation and serialization
    in ProfileDetailsForAdminPanelSchema() """

    creation_ts = datetime.now() - timedelta(days=86)

    sch1 = ProfileDetailsForAdminPanelSchema(
        user_id=544,
        created_at=creation_ts,
        updated_at=datetime.now() - timedelta(days=2),
        gender="not-specified",
        user=UserDetailsForAdminSchema(
            ID=544,
            username="golang_lover",
            is_active=True,
            is_superuser=False,
            email="test@example.com",
            created_at=creation_ts,
            updated_at=datetime.now() - timedelta(days=12)
        )
    )

    assert sch1.display_name is None and sch1.about is None
    assert sch1.user_id == sch1.user.ID
    assert sch1.created_at == sch1.user.created_at
    assert sch1.updated_at > sch1.created_at
    assert sch1.gender.name == "NS"
    assert sch1.user.is_active is True and sch1.user.is_superuser is False

    sch2 = ProfileDetailsForAdminPanelSchema(
        user_id=544,
        created_at=creation_ts,
        updated_at=datetime.now() - timedelta(days=2),
        gender="other",
        display_name="john doe",
        about="a long description ad bio or about.\n" * 4,
        birth_date=date(year=1988, month=6, day=29),
        links=[
            LinkListSchema(
                ID=8721,
                title="youtube",
                url="https://youtube.com/path/to/my/channel",
                profile_id=544
            ),
            LinkListSchema(
                ID=3467,
                title="github",
                url="https://github.com/hamidgh01",
                profile_id=544
            ),
        ],
        user=UserDetailsForAdminSchema(
            ID=544,
            username="golang_lover",
            is_active=True,
            is_superuser=False,
            email="test@example.com",
            created_at=creation_ts,
            updated_at=datetime.now() - timedelta(days=12)
        )
    )

    assert sch2.display_name is not None and sch2.about is not None
    assert type(sch2.birth_date) is date
    assert sch2.birth_date.strftime("%B") == "June"
    assert sch2.user_id == sch2.user.ID
    assert sch2.user_id == sch2.links[0].profile_id
    assert sch2.created_at == sch2.user.created_at
    assert sch2.gender.name == "OT" and sch2.gender.value == "other"
    assert sch2.links[0].title == "youtube"
    assert sch2.links[0].url.path == "/path/to/my/channel"
    assert sch2.links[1].title == "github"
    assert sch2.links[1].url.encoded_string() == "https://github.com/hamidgh01"
    assert sch2.user.email == "test@example.com"
    assert sch2.user.is_active is True and sch2.user.is_superuser is False
