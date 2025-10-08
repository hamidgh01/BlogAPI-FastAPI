""" Schemas (Pydantic models) for 'Post' & 'Tag' Models """

from typing import Annotated, List, Optional
from re import fullmatch

from pydantic import (
    BaseModel, Field, field_validator, ConfigDict
)

# --------------------------------------------------------------------

# Tag Schemas:


class CreateTagSchema(BaseModel):
    name: Annotated[str, Field(
        ..., min_length=1, max_length=120, description="unique tag name"
    )]

    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        if value and fullmatch(r"[ا-یa-zA-Z0-9_]{1,120}", value):
            raise ValueError("[name] allowed characters: "
                             "Persian/English Alphabets , numbers , _ ")
        return value


class ReadTagSchema(BaseModel):  # for both 'tag_list' and 'tag_details'
    id: Annotated[int, Field(..., description="unique tag ID")]
    name: Annotated[str, Field(..., description="unique tag name")]

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------

# Post Schemas: ...
