from sqlalchemy import Select, select
from typing import List, Tuple
from injector import Inject
from src.user import interfaces
from src.user.models import User
from src.core.unit_of_work import UnitOfWork


class UserRepository(interfaces.UserRepository):
    def __init__(self, unit_of_work: Inject[UnitOfWork]) -> None:
        self._unit_of_work = unit_of_work

    async def get_by_id(self, user_id: str) -> User:
        """
        Retrieve a user from the database by its ID.

        :param user_id: ID of the user to retrieve.
        :return: User object if found, None otherwise.
        """
        session = await self._unit_of_work.get_db_session()
        async with session.begin():
            result = await session.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
        return user

    async def login_with_email_and_pass(self, email, password):
        """
        Perform user login with email and password.

        :param email: Email address of the user.
        :param password: Password of the user.
        :return: User object if login is successful, None otherwise.
        """
        session = await self._unit_of_work.get_db_session()
        async with session.begin():
            result = await session.execute(
                select(User).filter(User.email == email, User.password == password)
            )
            user = result.scalars().first()
        return user

    async def update_token(self, user_id: int, token: str) -> None:
        """
        Update the JWT token associated with the user in the database.

        :param user_id: ID of the user whose token needs to be updated.
        :param token: New JWT token to be updated.
        """
        session = await self._unit_of_work.get_db_session()
        async with session.begin():
            user = await session.get(User, user_id)
            if user:
                user.token = token
                session.add(user)

    async def signup_user(self, user: User) -> None:
        session = await self._unit_of_work.get_db_session()
        session.add(user)
        await session.flush([user])

    async def get_token_by_email(self, email) -> User:
        """
        Retrieve a user's token from the database by its email address.

        :param email: Email address of the user.
        :return: User object if found, None otherwise.
        """
        session = await self._unit_of_work.get_db_session()
        async with session.begin():
            result = await session.execute(select(User).filter(User.email == email))
            user = result.scalars().first()
        return user

    async def save(self, user: User) -> None:
        session = await self._unit_of_work.get_db_session()
        session.add(user)
        await session.flush([user])

    def _get_base_query(self) -> Select[Tuple[User]]:
        return select(User)
