from typing import Sequence

from injector import inject
from sqlalchemy import select

from infrastructures.databases.master import DatabaseMasterSession
from modules.posts.dto import DCreatePost
from modules.posts.exception import FailedCreatePostError, FailedGetPostsError
from modules.posts.model import MPost


class SqlAlchemyPostRepository:
    @inject
    def __init__(self, session: DatabaseMasterSession):
        self._session = session

    async def get_posts(self) -> Sequence[MPost]:
        try:
            statement = select(MPost)
            posts = await self._session.scalars(statement)
            return posts.all()
        except Exception as exc:
            raise FailedGetPostsError from exc

    async def create_post(self, post: DCreatePost) -> MPost:
        try:
            model = MPost(title=post.title, content=post.content)

            self._session.add(model)
            await self._session.flush()
            await self._session.refresh(model)
        except Exception as exc:
            raise FailedCreatePostError from exc

        return model
