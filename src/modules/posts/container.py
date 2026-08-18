from injector import Binder, Module

from modules.posts.repositories.post import SqlAlchemyPostRepository
from modules.posts.repositories.protocol import PostRepository
from modules.posts.use_cases.create_post import CreatePostUseCase
from modules.posts.use_cases.get_posts import GetPostsUseCase


class CPostModule(Module):
    def configure(self, binder: Binder) -> None:
        self._register_repositories(binder)
        self._register_usecases(binder)

    def _register_repositories(self, binder: Binder) -> None:
        binder.bind(PostRepository, to=SqlAlchemyPostRepository)

    def _register_usecases(self, binder: Binder) -> None:
        binder.bind(CreatePostUseCase, to=CreatePostUseCase)
        binder.bind(GetPostsUseCase, to=GetPostsUseCase)
