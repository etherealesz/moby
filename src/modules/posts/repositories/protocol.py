from typing import Protocol, Sequence

from typing_extensions import runtime_checkable

from modules.posts.model import MPost
from modules.posts.dto import DCreatePost


@runtime_checkable
class PostRepository(Protocol):
    async def get_posts(self) -> Sequence[MPost]: ...
    async def create_post(self, post: DCreatePost) -> MPost: ...
