from _datetime import datetime, timezone, timedelta

from jose import jwt

from src.settings import ACCESS_TOKEN_SECRET_KEY, ACCESS_TOKEN_ALGORITHM
from src.user.errors import UserErrors
from injector import Inject
from src.core.use_cases import UseCase, UseCaseHandler
from src.user.schemas import (
    ResponseSignupSchema,
)
from src.user.services.user_repository import (
    UserRepository,
)


class Login(UseCase):
    email: str
    password: str

    class Handler(UseCaseHandler["Login", ResponseSignupSchema]):
        def __init__(
            self,
            user_repository: Inject[UserRepository],
        ) -> None:
            """
            Initializes the Login use case handler with the user repository dependency.

            :param user_repository: Instance of UserRepository for database interaction.
            """
            self._user_repository = user_repository

        async def execute(self, use_case: "Login") -> ResponseSignupSchema:
            """
            Executes the login use case.

            :param use_case: Instance of the Login use case.
            :return: ResponseSignupSchema containing the JWT token.
            """
            # Attempt to login with the provided email and password
            user = await self._user_repository.login_with_email_and_pass(
                email=use_case.email,
                password=use_case.password,
            )
            if not user:
                # If user is not found, raise an error
                raise UserErrors.EMAIL_OR_PASSWORD_INCORRECT
            # if the previous token is still valid
            is_valid = await self.validate_token(user.token)
            token = user.token if is_valid else self.generate_token(use_case.email)
            # Update the user's token in the database
            await self._user_repository.update_token(user.id, token)

            return await self.prepare_user_response(
                use_case.email, use_case.password, token
            )

        async def prepare_user_response(
            self, email: str, password: str, token: str
        ) -> ResponseSignupSchema:
            """
            Prepares the user response with the JWT token.

            :param email: Email of the user.
            :param password: Password of the user.
            :param token: JWT token.
            :return: ResponseSignupSchema containing the token.
            """
            # Attempt to login with the provided email and password
            user = await self._user_repository.login_with_email_and_pass(
                email, password
            )
            if not user:
                # If user is not found, raise an error
                raise UserErrors.USER_NOT_FOUND
            return ResponseSignupSchema(token=token, token_type="bearer")

        def generate_token(self, email: str) -> str:
            """
            Generates a JWT token for the provided email.

            :param email: Email for which token needs to be generated.
            :return: JWT token.
            """
            # Set the expiration time for the token
            expires_at = datetime.utcnow() + timedelta(hours=1)

            # Create a payload for the token
            payload = {"email": email, "exp": expires_at}

            return jwt.encode(
                payload, ACCESS_TOKEN_SECRET_KEY, algorithm=ACCESS_TOKEN_ALGORITHM
            )

        async def validate_token(self, token) -> bool:
            try:
                payload = jwt.decode(
                    token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ACCESS_TOKEN_ALGORITHM]
                )
                token_time = payload.get("exp")
                utc_now = datetime.now(timezone.utc)
                expiration_time_utc = datetime.utcfromtimestamp(token_time).replace(
                    tzinfo=timezone.utc
                )
                if expiration_time_utc > utc_now:
                    return True
            except (jwt.ExpiredSignatureError, jwt.JWTError, Exception):
                return False
