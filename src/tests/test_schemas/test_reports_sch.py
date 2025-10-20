from datetime import datetime, timedelta

from pydantic import ValidationError
import pytest

from src.schemas import (
    CreateReportOnUserSchema,
    CreateReportOnPostSchema
)
from src.schemas.admin import (
    # ReportOnUserListSchema,
    ReportOnUserDetailsSchema,  # includes all fields in ReportOnUserListSchema
    # ReportOnPostListSchema,
    ReportOnPostDetailsSchema  # includes all fields in ReportOnPostListSchema
)

# NOTE: there isn't any custom validator in 'Reports' related Schemas, so
# only the healthiness of these Schemas is tested here.


def test_healthiness_of_create_report_on_users_scheme():
    """
    test successful validation and serialization in CreateReportOnUserSchema()
    """

    rp_u_sch1 = CreateReportOnUserSchema(
        title="User-Report Reason 1",
        reported_user_id=234
    )
    rp_u_sch2 = CreateReportOnUserSchema(
        title="Other",
        description="a description about why reporter has reported a user...",
        reported_user_id=56343
    )
    assert rp_u_sch1.title.name == "R1"
    assert rp_u_sch1.description is None
    assert rp_u_sch1.reported_user_id == 234
    assert rp_u_sch2.title.name == "OT"
    assert "about why reporter has reported a user..." in rp_u_sch2.description
    assert rp_u_sch2.reported_user_id == 56343

    with pytest.raises(ValidationError) as err:
        CreateReportOnUserSchema(
            title="shit...",  # Not included in UserReportTitleChoices
            description="a description",
            reported_user_id=234
        )
    msg = "Input should be 'User-Report Reason 1', "
    assert msg in str(err.value)


def test_healthiness_of_create_report_on_posts_scheme():
    """
    test successful validation and serialization in CreateReportOnPostSchema()
    """

    rp_p_sch1 = CreateReportOnPostSchema(
        title="Post-Report Reason 1",
        reported_post_id=234
    )
    rp_p_sch2 = CreateReportOnPostSchema(
        title="Other",
        description="a description about why reporter has reported a post...",
        reported_post_id=56343
    )
    assert rp_p_sch1.title.name == "R1"
    assert rp_p_sch1.description is None
    assert rp_p_sch1.reported_post_id == 234
    assert rp_p_sch2.title.name == "OT"
    assert "about why reporter has reported a post..." in rp_p_sch2.description
    assert isinstance(rp_p_sch2.reported_post_id, int) is True

    with pytest.raises(ValidationError) as err:
        CreateReportOnPostSchema(
            title="shit...",  # Not included in UserReportTitleChoices
            description="a description",
            reported_user_id=234
        )
    msg = "Input should be 'Post-Report Reason 1', "
    assert msg in err.value.__str__()


def test_healthiness_of_both_reports_details_schemas():
    """ test successful validation and serialization in
    ReportOnPostDetailsSchema() and ReportOnUserDetailsSchema() """

    now_ = datetime.now()

    rp_u_dt_sch = ReportOnUserDetailsSchema(
        ID=6543,
        reporter_id=765434,
        reported_user_id=21345,
        title="User-Report Reason 1",
        created_at=now_,
    )
    assert type(rp_u_dt_sch.ID) is int
    assert isinstance(rp_u_dt_sch.reporter_id, int) is True
    assert isinstance(rp_u_dt_sch.reported_user_id, int) is True
    assert rp_u_dt_sch.description is None
    assert rp_u_dt_sch.title.name == "R1"
    assert type(rp_u_dt_sch.created_at) is datetime

    rp_p_dt_sch = ReportOnPostDetailsSchema(
        ID=2345987,
        reporter_id=4444444333333,
        reported_user_id=2345678999999,
        title="Other",
        description="some text as report description",
        created_at=now_ - timedelta(days=12, hours=17),
    )
    assert type(rp_p_dt_sch.ID) is int
    assert rp_p_dt_sch.reporter_id, int == 4444444333333
    assert type(rp_p_dt_sch.reported_user_id) is int
    assert rp_p_dt_sch.description is not None
    assert rp_p_dt_sch.title.name.lower() == "ot"
    assert isinstance(rp_p_dt_sch.created_at, datetime) is True
