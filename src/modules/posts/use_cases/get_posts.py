from injector import inject

from infrastructures.databases.master import DatabaseMasterSession
from modules.posts.repositories.protocol import PostRepository


class GetPostsUseCase:
    @inject
    def __init__(
        self,
        session: DatabaseMasterSession,
        repository: PostRepository,
    ):
        self._session = session
        self._repository = repository

    async def execute(self):
        async with self._session.begin():
            posts = await self._repository.get_posts()

        return posts
