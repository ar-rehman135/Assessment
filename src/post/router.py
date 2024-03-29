from datetime import datetime
from typing import Annotated
from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi_injector import Injected
from src.core.auth import require_valid_access_token
from src.post.schemas import (
    AddPostResponseSchema,
    PostResponseSchema,
    DeletePostResponse,
)
from src.post.use_cases.create_a_post import CreateAPost
from src.post.use_cases.delete_a_post import DeleteAPost
from src.post.use_cases.get_posts import GetAllPosts
from src.core.use_cases import UseCase

# Initialize cache
cache = TTLCache(maxsize=1000, ttl=300)

# Initialize API router
router = APIRouter(
    prefix="/post", tags=["posts"], dependencies=[Depends(require_valid_access_token)]
)


async def get_access_token(request: Request):
    """
    Function to extract and validate the access token from the request headers.

    Args:
        request (Request): The incoming request object.

    Returns:
        str: The extracted access token.

    Raises:
        HTTPException: If the authorization header is missing or invalid.
    """
    authorization = request.headers.get("Authorization")
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    try:
        token_type, token = authorization.split()
        if token_type.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")


class AnnotatedCreatePost(UseCase):
    title: Annotated[str, Body()]
    description: Annotated[str, Body()]
    created_at: Annotated[datetime, Body()]


@router.post("/", description="Create a post", response_model=AddPostResponseSchema)
async def create_a_post(
    use_case: Annotated[AnnotatedCreatePost, Body()],
    handler: Annotated[CreateAPost.Handler, Injected(CreateAPost.Handler)],
    request: Request,
) -> AddPostResponseSchema:
    """
    Endpoint to create a new post.

    Args:
        use_case (CreateAPost): The use case instance for creating a post.
        handler (CreateAPost.Handler): The handler for executing the use case.
        request (Request): The incoming request object.

    Returns:
        AddPostResponseSchema: The response schema containing the ID of the created post.

    Raises:
        HTTPException: If the payload size exceeds 1 MB.
    """
    total_size = len(use_case.json())
    if total_size > 1024 * 1024:
        raise HTTPException(status_code=413, detail="Payload size exceeds 1 MB")
    token = await get_access_token(request)
    use_case_dict = dict(use_case)
    return await handler.execute(CreateAPost(**use_case_dict, token=token))


@router.get(
    "/", description="Get all posts", response_model=list[PostResponseSchema] | None
)
async def get_all_post(
    use_case: Annotated[GetAllPosts, Depends()],
    handler: Annotated[GetAllPosts.Handler, Injected(GetAllPosts.Handler)],
    request: Request,
):
    """
    Endpoint to retrieve all posts.

    Args:
        use_case (GetAllPosts): The use case instance for getting all posts.
        handler (GetAllPosts.Handler): The handler for executing the use case.
        request (Request): The incoming request object.

    Returns:
        list[PostResponseSchema]: The response schema containing a list of post data.
    """
    url_key = str(request.headers.get("authorization"))
    cached_data = cache.get(url_key)
    if cached_data:
        return cache.get("data")  # Return cached data directly
    token = await get_access_token(request)
    use_case.token = token
    response_data = await handler.execute(use_case)
    if response_data:
        cache[url_key] = url_key
        cache["data"] = response_data
        return response_data


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    description="Delete a post",
    response_model=DeletePostResponse,
)
async def delete_a_post(
    post_id: str,
    handler: Annotated[DeleteAPost.Handler, Injected(DeleteAPost.Handler)],
    request: Request,
) -> DeletePostResponse:
    """
    Endpoint to delete a post.

    Args:
        post_id (DeleteAPost): The use case instance for deleting a post.
        handler (DeleteAPost.Handler): The handler for executing the use case.
        request (Request): The incoming request object.

    Returns:
        DeletePostResponse: The response indicating the success of the operation.
    """
    token = await get_access_token(request)
    return await handler.execute(DeleteAPost(token=token, post_id=post_id))
