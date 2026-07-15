from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi_injector import Injected
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.schemas.predefined import SStandardValidationErrorResponse
from app.schemas.response import SStandardListResponse, SStandardResponse
from app.utils.standard_response_builder import StandardResponseBuilder
from core.logger.factory import create_app_logger
from modules.posts.exception import FailedCreatePostError, FailedGetPostsError
from modules.posts.mapper.post import map_post_schema_from_post_model
from modules.posts.schemas.request import SPostPostsRequest
from modules.posts.schemas.response import SPost
from modules.posts.use_cases.create_post import CreatePostUseCase
from modules.posts.use_cases.get_posts import GetPostsUseCase

tags: List = ["API / Posts"]
router = APIRouter(prefix="/posts", tags=tags)

logger = create_app_logger()


@router.get("", status_code=status.HTTP_200_OK)
async def list_posts(
    get_posts=Injected(GetPostsUseCase),
) -> SStandardListResponse[SPost]:
    logger.debug("Logging example")

    try:
        posts = await get_posts.execute()
    except FailedGetPostsError as exc:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    response_data = [map_post_schema_from_post_model(post) for post in posts]
    return SStandardListResponse(data=response_data)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": SStandardValidationErrorResponse}
    },
)
async def create_post(
    body: SPostPostsRequest,
    create_post=Injected(CreatePostUseCase),
) -> SStandardResponse[SPost]:
    try:
        post = await create_post.execute(title=body.title, content=body.content)
    except FailedCreatePostError as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    response_data = map_post_schema_from_post_model(post)
    return StandardResponseBuilder().set_data(response_data).build()
