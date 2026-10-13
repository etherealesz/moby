from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructures.persistence.model.base import AbstractModel
from infrastructures.persistence.model.mixin import TimestampMixin

if TYPE_CHECKING:
    from modules.waste_categories.models.waste_subcategory import WasteSubcategory


class WasteCategory(AbstractModel, TimestampMixin):
    """Tabel Waste_Category (Lampiran 9). category_id = indeks label model + 1."""

    __tablename__ = "waste_category"

    category_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    category_name: Mapped[str] = mapped_column(String(50), nullable=False)
    category_code: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)

    subcategories: Mapped[list["WasteSubcategory"]] = relationship(
        "WasteSubcategory",
        back_populates="category",
        lazy="noload",
        order_by="WasteSubcategory.subcategory_id",
    )
