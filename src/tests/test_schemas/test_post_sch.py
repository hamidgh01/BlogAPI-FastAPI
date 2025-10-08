from pydantic import ValidationError
import pytest

from src.schemas import (
    CreateTagSchema,
    ReadTagSchema,
    CreatePostSchema,
    UpdatePostSchema,
    ChangePostPrivacySchema,
    UpdatePostStatusSchema
)

# NOTE: there isn't any custom validator in 'Post' related Schemas, so
# only the healthiness of these Schemas is tested here.


@pytest.mark.parametrize(
    argnames="invalid_tag_name, exp_type, expected",
    argvalues=[
        # NOTE: expected pattern -> r'[ا-یa-zA-Z0-9_]{1,120}'
        (
            "abc" * 41,
            ValidationError,  # why ValidationError? -> explained in Schema
            "String should have at most 120 characters"
        ),
        ("tag name", ValueError, "|  allowed characters: "),
        ("test-", ValueError, "Persian/English Alphabets"),
        ("test!", ValueError, " , numbers , _ "),
        ("python 2", ValueError, " , numbers , _ ")
    ]
)
def test_invalid_tag_name_patterns(invalid_tag_name, exp_type, expected):
    with pytest.raises(exp_type) as err:
        CreateTagSchema(name=invalid_tag_name)
    assert expected in err.value.__str__()


def test_healthiness_of_create_tag_schema_and_read_tag_scheme():
    """ test successful validation and serialization in
    CreateTagSchema() and ReadTagSchema with valid 'tag name' """

    tag_sch1 = CreateTagSchema(name="Python3")
    tag_sch2 = CreateTagSchema(name="System_Design")
    tag_sch3 = CreateTagSchema(name="زبان_پارسی")
    assert tag_sch1.name == "Python3"
    assert tag_sch2.name == "System_Design"
    assert tag_sch3.name == "زبان_پارسی"

    tag_sch4 = ReadTagSchema(id=1, name="Python3")
    tag_sch5 = ReadTagSchema(id=2765, name="System_Design")
    tag_sch6 = ReadTagSchema(id=11234, name="زبان_پارسی")
    assert tag_sch4.id == 1
    assert tag_sch4.name == "Python3"
    assert tag_sch5.name == "System_Design"
    assert tag_sch6.name == "زبان_پارسی"


def test_healthiness_of_create_post_schema():
    """ test successful validation and serialization in CreatePostSchema() """

    post_sch1 = CreatePostSchema(
        title="test title",
        content="test long text as title.\n" * 10,
    )
    assert post_sch1.title == "test title"
    assert "test long text as title." in post_sch1.content
    assert post_sch1.is_private is False
    assert post_sch1.status.value == "draft"
    assert post_sch1.tags is None

    post_sch2 = CreatePostSchema(
        title="test title",
        content="test long text as title.\n" * 10,
        is_private=True,
        status="published",
        tags=[123, "Python3", "Asynchronous_Programming", "پارسی"]
    )
    assert post_sch2.is_private is True
    assert post_sch2.status.value == "published"
    assert 123 in post_sch2.tags
    assert "Python3" in post_sch2.tags
    assert post_sch2.tags[2] == "Asynchronous_Programming"
    assert "پارسی" in post_sch2.tags


def test_healthiness_of_update_post_schema():
    """ test successful validation and serialization in UpdatePostSchema() """

    upd_post_sch1 = UpdatePostSchema()
    assert upd_post_sch1.title is None
    assert upd_post_sch1.content is None
    assert upd_post_sch1.is_private is False
    assert upd_post_sch1.tags is None

    upd_post_sch2 = UpdatePostSchema(
        title="test title",
        content="test long text as title.\n" * 10,
        is_private=True,
        tags=[123, "Python3", "Asynchronous_Programming", "پارسی"]
    )
    assert upd_post_sch2.title == "test title"
    assert "test long text as title." in upd_post_sch2.content
    assert upd_post_sch2.is_private is True
    assert 123 in upd_post_sch2.tags
    assert "Python3" in upd_post_sch2.tags
    assert upd_post_sch2.tags[2] == "Asynchronous_Programming"
    assert "پارسی" in upd_post_sch2.tags


def test_healthiness_of_change_post_privacy_schema():
    """
    test successful validation and serialization in ChangePostPrivacySchema()
    """
    ch_pv_sch1 = ChangePostPrivacySchema(is_private=True)
    ch_pv_sch2 = ChangePostPrivacySchema(is_private=False)
    assert ch_pv_sch1.is_private is True
    assert ch_pv_sch2.is_private is False


def test_healthiness_of_update_post_status_schema():
    """
    test successful validation and serialization in UpdatePostStatusSchema()
    """
    up_st_sch1 = UpdatePostStatusSchema(status="draft")
    up_st_sch2 = UpdatePostStatusSchema(status="published")
    up_st_sch3 = UpdatePostStatusSchema(status="rejected")
    up_st_sch4 = UpdatePostStatusSchema(status="deleted-by-author")
    assert up_st_sch1.status.value == "draft"
    assert up_st_sch2.status.value == "published"
    assert up_st_sch3.status.value == "rejected"
    assert up_st_sch4.status.value == "deleted-by-author"
