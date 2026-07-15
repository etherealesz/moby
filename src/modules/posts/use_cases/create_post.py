from injector import inject

from infrastructures.databases.master import DatabaseMasterSession
from modules.posts.dto import DCreatePost
from modules.posts.model import MPost
from modules.posts.repositories.protocol import PostRepository


class CreatePostUseCase:
    @inject
    def __init__(self, session: DatabaseMasterSession, post_repository: PostRepository):
        self._session = session
        self._post_repository = post_repository

    async def execute(self, title: str, content: str) -> MPost:
        post = DCreatePost(title=title, content=content)
        async with self._session.begin():
            return await self._post_repository.create_post(post)
