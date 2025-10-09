from datetime import datetime, timedelta

from pydantic import ValidationError
import pytest

from src.schemas import (
    CreateCommentSchema,
    UpdateCommentContentSchema,
    UpdateCommentStatusSchema,
    # CommentListSchema,
    CommentDetailsSchema  # includes all fields in CommentListSchema
)

# NOTE: there isn't any custom validator in 'Comment' related Schemas, so
# only the healthiness of these Schemas is tested here.


def test_healthiness_of_create_comment_scheme():
    """test successful validation and serialization in CreateCommentSchema()"""

    cm_sch1 = CreateCommentSchema(
        content="something as comment content.\n" * 7,
        parent_type="post",
        parent_id=1234
    )
    cm_sch2 = CreateCommentSchema(
        content="something text.\n" * 4,
        parent_type="comment",
        parent_id=765
    )

    assert "as comment content.\nsomething as comme" in cm_sch1.content
    assert cm_sch1.parent_type.value == "post"
    assert cm_sch1.parent_type.name == "P"
    assert cm_sch1.parent_id == 1234
    assert "something text.\nsomething text.\n" in cm_sch2.content
    assert cm_sch2.parent_type.value == "comment"
    assert cm_sch2.parent_type.name == "C"
    assert cm_sch2.parent_id == 765

    with pytest.raises(ValidationError) as err:
        CreateCommentSchema(
            content="something text.\n" * 4,
            parent_type="shit...",  # Not included in ParentType Enum
            parent_id=765
        )

    assert "Input should be 'post' or 'comment'" in str(err.value)


def test_healthiness_of_update_comment_content_schema():
    """ test successful validation and serialization
    in UpdateCommentContentSchema() """

    up_cm_sch1 = UpdateCommentContentSchema()
    up_cm_sch2 = UpdateCommentContentSchema(
        content="updated comment content. " * 3
    )
    assert up_cm_sch1.content is None
    assert " comment content. updated comment content." in up_cm_sch2.content


def test_healthiness_of_update_comment_status_schema():
    """ test successful validation and serialization
    in UpdateCommentStatusSchema() """

    up_cm_st_sch1 = UpdateCommentStatusSchema(status="published")
    up_cm_st_sch2 = UpdateCommentStatusSchema(status="Hidden-by-Admin")
    up_cm_st_sch3 = UpdateCommentStatusSchema(status="Deleted-By-Commenter")
    assert up_cm_st_sch1.status.value == "published"
    assert up_cm_st_sch1.status.name == "PB"
    assert up_cm_st_sch2.status.value == "Hidden-by-Admin"
    assert "Deleted" in up_cm_st_sch3.status.value
    assert up_cm_st_sch3.status.name == "DL"


def test_healthiness_of_comment_details_schema():
    """
    test successful validation and serialization in CommentDetailsSchema()
    """
    yesterday = datetime.now() - timedelta(days=1)
    cm_dt_sch1 = CommentDetailsSchema(
        id=1265,
        user_id=654312345,
        content="a long text (maximum = 1000 characters) as comment. \n" * 10,
        status="published",
        created_at=yesterday,
        updated_at=yesterday + timedelta(hours=6),
        parent_type="post",
        parent_id=898454,
    )
    assert cm_dt_sch1.id == 1265
    assert cm_dt_sch1.user_id == 654312345
    assert " as comment. \na long text (maximum = 1000 c" in cm_dt_sch1.content
    assert cm_dt_sch1.status.value == "published"
    assert cm_dt_sch1.status.name == "PB"
    assert cm_dt_sch1.created_at == yesterday
    assert cm_dt_sch1.updated_at > (cm_dt_sch1.created_at + timedelta(hours=5))
    assert cm_dt_sch1.parent_type.value == "post"
    assert cm_dt_sch1.parent_type.name == "P"
    assert cm_dt_sch1.parent_id == 898454
