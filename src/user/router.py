from typing import Annotated
from pydantic import EmailStr

from fastapi import APIRouter, Body
from fastapi_injector import Injected
from src.core.use_cases import UseCase


from src.user.schemas import (
    ResponseSignupSchema,
)
from src.user.use_cases import (
    SignupUser,
    Login,
)

router = APIRouter(
    prefix="/user",
    tags=[""],
    # dependencies=[
    #     Depends(require_organization_access_token),
    # ],
)


class AnnotatedSignup(UseCase):
    email: Annotated[EmailStr, Body()]
    password: Annotated[str, Body()]


@router.post("/signup", description="Signup")
async def signup(
    use_case: Annotated[AnnotatedSignup, Body()],
    handler: Annotated[SignupUser.Handler, Injected(SignupUser.Handler)],
) -> ResponseSignupSchema:
    use_case_dict = dict(use_case)
    return await handler.execute(SignupUser(**use_case_dict))


@router.post("/login", description="Endpoint to authenticate and login a user.")
async def login(
    use_case: Annotated[AnnotatedSignup, Body()],
    handler: Annotated[Login.Handler, Injected(Login.Handler)],
) -> ResponseSignupSchema:
    use_case_dict = dict(use_case)
    return await handler.execute(Login(**use_case_dict))
