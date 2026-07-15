from modules.posts.model import MPost
from modules.posts.schemas.response import SPost


def map_post_schema_from_post_model(model: MPost) -> SPost:
    return SPost(
        id=model.id,
        title=model.title,
        content=model.content,
        uploaded_at=model.created_at,
    )
