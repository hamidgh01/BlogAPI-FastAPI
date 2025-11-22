from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str


# Note: tests for 'Token' and 'Message' added in 'test_schemas/test_user.py'
