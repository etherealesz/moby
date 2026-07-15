from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructures.persistence.model.base import PersistentModel


class MPost(PersistentModel):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    views: Mapped[int] = mapped_column(server_default="0")
