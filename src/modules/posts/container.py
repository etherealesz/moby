from injector import Binder, Module, singleton

from modules.posts.repositories.izmo_auth_api_auth import IzmoAuthAPIAuthRepository
from modules.posts.repositories.izmo_post import IzmoPostRepository
from modules.posts.repositories.protocol import AuthRepository, PostRepository
from modules.posts.use_cases.create_post import CreatePostUseCase
from modules.posts.use_cases.get_posts import GetPostsUseCase


class CPostModule(Module):
    def configure(self, binder: Binder) -> None:
        self._register_repositories(binder)
        self._register_usecases(binder)

    def _register_repositories(self, binder: Binder) -> None:
        binder.bind(AuthRepository, to=IzmoAuthAPIAuthRepository, scope=singleton)
        binder.bind(PostRepository, to=IzmoPostRepository)

    def _register_usecases(self, binder: Binder) -> None:
        binder.bind(CreatePostUseCase, to=CreatePostUseCase)
        binder.bind(GetPostsUseCase, to=GetPostsUseCase)
