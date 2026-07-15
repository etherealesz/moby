from datetime import datetime
from unittest.mock import AsyncMock

from infrastructures.databases.master.session import DatabaseMasterSession
from modules.posts.model import MPost
from modules.posts.use_cases.get_posts import GetPostsUseCase


async def test_get_posts(mock_database_master_session: DatabaseMasterSession):
    mock_post_repository = AsyncMock()
    mock_post_repository.get_posts.return_value = [
        MPost(
            id=1,
            title="Post 1",
            content="This is the content of mock post 1.",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        MPost(
            id=2,
            title="Post 2",
            content="This is the content of mock post 2.",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]

    get_posts = GetPostsUseCase(
        session=mock_database_master_session,
        post_repository=mock_post_repository,
    )
    data = await get_posts.execute()
    assert len(data) == 2
    assert data[0].title == "Post 1"
    assert data[1].title == "Post 2"
