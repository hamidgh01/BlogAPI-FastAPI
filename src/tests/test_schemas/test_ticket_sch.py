from datetime import datetime

from pydantic import ValidationError
import pytest

from src.schemas import (
    CreateTicketSchema,
    UpdateTicketStatusForAdminSchema,
    # TicketListSchema,
    TicketDetailsSchema  # includes all fields in TicketListSchema
)

# NOTE: there isn't any custom validator in 'Ticket' related Schemas, so
# only the healthiness of these Schemas is tested here.


def test_healthiness_of_create_ticket_scheme():
    """test successful validation and serialization in CreateTicketSchema()"""

    ticket_sch1 = CreateTicketSchema(
        subject="something as subject", message="some text " * 10
    )
    ticket_sch2 = CreateTicketSchema(message="some another text " * 10)
    assert ticket_sch1.subject == "something as subject"
    assert "some text some text " in ticket_sch1.message
    assert ticket_sch2.subject is None
    assert " another text some another " in ticket_sch2.message

    with pytest.raises(ValidationError) as err:
        CreateTicketSchema(
            subject="something " * 20,  # more than 120 characters
            message="some text " * 10
        )

    assert "String should have at most 120 characters" in str(err.value)


def test_healthiness_of_update_ticket_status_for_admin_schema():
    """ test successful validation and serialization
    in UpdateTicketStatusForAdminSchema() """

    t_st_sch1 = UpdateTicketStatusForAdminSchema(status="read")
    t_st_sch2 = UpdateTicketStatusForAdminSchema(status="unread")
    t_st_sch3 = UpdateTicketStatusForAdminSchema(status="closed")
    assert t_st_sch1.status.value == "read" and t_st_sch1.status.name == "R"
    assert t_st_sch2.status.value == "unread" and t_st_sch2.status.name == "N"
    assert t_st_sch3.status.value == "closed" and t_st_sch3.status.name == "C"

    with pytest.raises(ValidationError) as err:
        UpdateTicketStatusForAdminSchema(status="shit...")
    msg = "Input should be 'unread', 'read' or 'closed'"
    assert msg in err.value.__str__()


def test_healthiness_of_ticket_details_schema():
    """test successful validation and serialization in TicketDetailsSchema()"""

    now_ = datetime.now()
    t_dt_sch1 = TicketDetailsSchema(
        id=1265,
        subject="something as title",
        message="a long text (maximum = 4000 characters) as message. \n" * 20,
        status="unread",
        created_at=now_,
        user_id=89236423
    )
    assert t_dt_sch1.id == 1265
    assert t_dt_sch1.subject == "something as title"
    assert "as message. \na long text (maximum = 4000" in t_dt_sch1.message
    assert t_dt_sch1.status.value == "unread" and t_dt_sch1.status.name == "N"
    assert t_dt_sch1.created_at == now_
    assert t_dt_sch1.user_id == 89236423

    t_dt_sch2 = TicketDetailsSchema(
        id=1265,
        message="a long text (maximum = 4000 characters) as message. \n" * 20,
        status="unread",
        created_at=now_,
    )
    assert t_dt_sch2.subject is None
    assert t_dt_sch2.user_id is None
