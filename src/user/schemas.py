from pydantic import BaseModel


class RequestSignupSchema(BaseModel):
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class ResponseSignupSchema(BaseModel):
    token: str  # noqa: A003

    class Config:
        from_attributes = True


class SuccessResponseSchema(BaseModel):
    status: str
