from typing import Protocol, runtime_checkable

from src.user.models import User
from src.user.schemas import ResponseSignupSchema


@runtime_checkable
class UserRepository(Protocol):
    async def get_by_id(self, user_id: str) -> ResponseSignupSchema | None:
        ...

    async def signup_user(
        self,
        user: User,
    ) -> None:
        ...

    async def save(
        self,
        user: User,
    ) -> None:
        ...
