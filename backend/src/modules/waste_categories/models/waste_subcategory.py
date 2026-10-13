from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructures.persistence.model.base import AbstractModel
from infrastructures.persistence.model.mixin import TimestampMixin

if TYPE_CHECKING:
    from modules.waste_categories.models.waste_category import WasteCategory


class WasteSubcategory(AbstractModel, TimestampMixin):
    """Tabel Waste_Subcategory (Lampiran 9), 17 subkelas pada Tabel 2.1."""

    __tablename__ = "waste_subcategory"

    subcategory_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("waste_category.category_id"), nullable=False
    )
    subcategory_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)

    category: Mapped["WasteCategory"] = relationship(
        "WasteCategory",
        back_populates="subcategories",
        lazy="noload",
    )
