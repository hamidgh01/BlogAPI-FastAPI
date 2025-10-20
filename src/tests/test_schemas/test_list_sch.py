from datetime import datetime, timedelta

from pydantic import ValidationError
import pytest

from src.schemas import (
    CreateListSchema,
    UpdateListSchema,
    # ListListSchema,
    ListDetailsSchema,  # includes all fields in ListListSchema
    SaveOrUnsavePost,
    SaveOrUnsaveList
)

# NOTE: there isn't any custom validator in 'List' related Schemas, so
# only the healthiness of these Schemas is tested here.


def test_healthiness_of_create_list_scheme():
    """test successful validation and serialization in CreateListSchema()"""

    ls_sch1 = CreateListSchema(title="title of list")
    ls_sch2 = CreateListSchema(
        title="Golang Backend",
        description="this playlist includes article about backend dev in go",
        is_private=False,
        post_id=45643
    )
    assert ls_sch1.title == "title of list"
    assert ls_sch1.description is None and ls_sch1.post_id is None
    assert ls_sch1.is_private is True
    assert "Golang" in ls_sch2.title
    assert "about backend dev in go" in ls_sch2.description
    assert ls_sch2.is_private is False and ls_sch2.post_id == 45643

    with pytest.raises(ValidationError) as err:
        CreateListSchema(title="something as a long title..." * 5)
    assert "String should have at most 120 characters" in str(err.value)


def test_healthiness_of_update_list_schema():
    """test successful validation and serialization in UpdateListSchema()"""

    up_ls_sch1 = UpdateListSchema()
    up_ls_sch2 = UpdateListSchema(title="System Design", is_private=False)
    assert up_ls_sch1.title is None
    assert up_ls_sch1.description is None
    assert up_ls_sch1.is_private is None
    assert up_ls_sch2.title == "System Design"
    assert up_ls_sch2.is_private is False


def test_healthiness_of_list_details_schema():
    """test successful validation and serialization in ListDetailsSchema()"""

    now_ = datetime.now()
    one_mont_age = now_ - timedelta(days=30)
    ls_dt_sch = ListDetailsSchema(
        id=1234,
        title="Developing HTTP server with Golang seri",
        description="this playlist includes a seri of posts explaining the "
                    "development process of an HTTP server step-by-step...",
        is_private=False,
        created_at=one_mont_age,
        user_id=752443,
        post_count=32,
        saved_by_viewer=True
    )
    assert type(ls_dt_sch.id) is int
    assert "HTTP server with Golang" in ls_dt_sch.title
    assert "seri of posts explaining the development" in ls_dt_sch.description
    assert ls_dt_sch.is_private is False
    assert isinstance(ls_dt_sch.created_at, datetime) is True
    assert ls_dt_sch.user_id == 752443
    assert ls_dt_sch.post_count == 32
    assert ls_dt_sch.saved_by_viewer is True


def test_healthiness_of_save_or_unsave_for_both_posts_and_lists_schema():
    """ test successful validation and serialization in both
    SaveOrUnsavePost() and SaveOrUnsaveList() """

    sch1 = SaveOrUnsavePost(post_id=345, list_id=6543567)
    sch2 = SaveOrUnsaveList(list_id=12)
    assert type(sch1.post_id) is int and sch1.list_id == 6543567
    assert isinstance(sch2.list_id, int) is True
