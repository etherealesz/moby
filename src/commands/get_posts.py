from injector import Injector

from core.logger.factory import create_app_logger
from modules.posts.use_cases.get_posts import GetPostsUseCase

logger = create_app_logger()


async def execute(injector: Injector):
    get_posts = injector.get(GetPostsUseCase)
    posts = await get_posts.execute()
    logger.info(f"Retrieved {len(posts)} posts", extra={"posts": posts})
