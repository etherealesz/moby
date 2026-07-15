from typing import Protocol, Sequence, runtime_checkable

from modules.posts.model import MCreatePost, MPost


@runtime_checkable
class PostsRepository(Protocol):
    async def get_posts(self) -> Sequence[MPost]: ...
    async def create(self, post: MCreatePost) -> MPost: ...
