import uuid
from typing import Optional
from src.core.errors import AuthErrors
from src.settings import (
    ACCESS_TOKEN_ALGORITHM,
    ACCESS_TOKEN_SECRET_KEY,
    OAUTH_TOKEN_URL,
)
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from injector import Inject
import jwt
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from src.core.use_cases import UseCase, UseCaseHandler
from src.post.errors import PostErrors
from src.post.services.post_repository import PostRepository
from src.post.schemas import Post, AddPostResponseSchema
from src.post.models import Post as postDBModel
from src.user.models import User
from src.user.services.user_repository import UserRepository

# OAuth2 password bearer flow for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=OAUTH_TOKEN_URL)


class CreateAPost(UseCase):
    """Use case to create a post."""

    title: str  # Title of the post
    description: str  # Description of the post
    created_at: datetime
    token: Optional[str] = Depends(oauth2_scheme)

    class Handler(UseCaseHandler["CreateAPost", Post]):
        """Handler for the create post use case."""

        def __init__(
            self,
            post_repository: Inject[PostRepository],
            user_repository: Inject[UserRepository],
        ) -> None:
            self._post_repository = post_repository
            self._user_repository = user_repository

        async def execute(
            self,
            use_case: "CreateAPost",
        ) -> AddPostResponseSchema:
            """Execute the use case to create a post.

            Args:
            - use_case: The use case instance containing post details.

            Returns:
            - AddPostResponseSchema: The response schema containing the created post ID.
            """
            # Verify token validity
            user = await self.verify_token(use_case.token)
            if user:
                # Generate a unique ID for the post
                post_id = str(uuid.uuid4())
                created_at_str = str(use_case.created_at)
                # Create a database model instance for the post
                post = postDBModel(
                    id=post_id,
                    title=use_case.title,
                    description=use_case.description,
                    created_at=created_at_str,
                    created_by_id=user.id,
                )
                # Save the post in the database
                post_id = await self.create_post(post)
                return await self.prepare_post_response(post_id)

        async def create_post(self, post: postDBModel) -> int:
            """Create a post in the database.

            Args:
            - post: The post model instance to be created.

            Returns:
            - int: The ID of the created post.
            """
            try:
                return await self._post_repository.create(post)
            except IntegrityError as e:
                raise PostErrors.POST_ALREADY_EXISTS from e

        async def prepare_post_response(self, post_id) -> AddPostResponseSchema:
            """Prepare the response containing the created post ID.

            Args:
            - post_id: The ID of the created post.

            Returns:
            - AddPostResponseSchema: The response schema containing the created post ID.
            """
            # Retrieve the post by its ID
            post = await self._post_repository.get_by_id(post_id)
            if not post:
                # If post not found, raise error
                raise PostErrors.POST_NOT_FOUND
            return AddPostResponseSchema(post_id=post.id)

        async def verify_token(self, token: str = Depends(oauth2_scheme)) -> User:
            """Verify the access token.

            Args:
            - token: The access token to be verified.

            Returns:
            - User: The user associated with the token if valid.
            """
            try:
                # Decode the access token
                payload = jwt.decode(
                    token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ACCESS_TOKEN_ALGORITHM]
                )
                email: str = payload.get("email")
                if email is None:
                    # If email not found in token, raise error
                    raise HTTPException(
                        status_code=401, detail=AuthErrors.ACCESS_TOKEN_INVALID
                    )
                else:
                    # Check if the email is valid
                    return await self._user_repository.get_token_by_email(email)
            except jwt.ExpiredSignatureError as e:
                # If token has expired, raise error
                raise HTTPException(
                    status_code=401, detail=AuthErrors.ACCESS_TOKEN_INVALID
                ) from e
            except jwt.DecodeError as e:
                # If token decoding fails, raise error
                raise HTTPException(
                    status_code=401, detail=AuthErrors.ACCESS_TOKEN_DECODE_ERROR
                ) from e
