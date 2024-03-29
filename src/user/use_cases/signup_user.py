import uuid
import datetime
import jwt
from injector import Inject
from sqlalchemy.exc import IntegrityError
from src.core.use_cases import UseCase, UseCaseHandler
from src.user.models import User
from src.user.schemas import (
    RequestSignupSchema,
    ResponseSignupSchema,
)
from src.user.services.user_repository import (
    UserRepository,
)
from src.user.errors import UserErrors
from src.settings import (
    ACCESS_TOKEN_SECRET_KEY,
    ACCESS_TOKEN_ALGORITHM,
    ACCESS_TOKEN_Time_DELTA,
)


class SignupUser(UseCase):
    email: str
    password: str

    class Handler(UseCaseHandler["SignupUser", RequestSignupSchema]):
        def __init__(
            self,
            user_repository: Inject[UserRepository],
        ) -> None:
            self._user_repository = user_repository

        async def execute(self, use_case: "SignupUser") -> ResponseSignupSchema:
            user_id = str(uuid.uuid4())

            user = User(
                id=user_id,
                email=use_case.email,
                password=use_case.password,
                token=self.generate_token(use_case.email),
            )
            await self.create_user(user)
            return ResponseSignupSchema(token=user.token)

        async def create_user(self, user: User) -> None:
            try:
                await self._user_repository.signup_user(user)
            except IntegrityError as e:
                raise UserErrors.EMAIL_ALREADY_EXISTS from e

        def generate_token(self, email: str) -> str:
            """
            Generates a JWT token for the provided email.

            :param email: Email for which token needs to be generated.
            :return: JWT token.
            """
            # Set the expiration time for the token
            expires_at = datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(hours=1)

            # Create a payload for the token
            payload = {"email": email, "exp": expires_at}

            return jwt.encode(
                payload, ACCESS_TOKEN_SECRET_KEY, algorithm=ACCESS_TOKEN_ALGORITHM
            )
