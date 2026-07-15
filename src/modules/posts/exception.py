from core.exceptions.base import ApplicationError


class FailedGetPostsError(ApplicationError):
    def __init__(self):
        super().__init__("GET_POSTS_FAILED")


class FailedCreatePostError(ApplicationError):
    def __init__(self):
        super().__init__("CREATE_POST_FAILED")
