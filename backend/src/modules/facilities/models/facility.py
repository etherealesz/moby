from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructures.persistence.model.base import AbstractModel
from infrastructures.persistence.model.mixin import TimestampMixin

if TYPE_CHECKING:
    from modules.waste_categories.models.waste_category import WasteCategory


class Facility(AbstractModel, TimestampMixin):
    """Tabel Facility (Lampiran 9). facility_type: Bank Sampah / TPS3R / TPST / TPA."""

    __tablename__ = "facility"

    facility_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    facility_name: Mapped[str] = mapped_column(String(100), nullable=False)
    facility_type: Mapped[str] = mapped_column(String(20), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    address: Mapped[str | None] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)

    categories: Mapped[list["WasteCategory"]] = relationship(
        "WasteCategory",
        secondary="facility_category",
        lazy="noload",
        order_by="WasteCategory.category_id",
        viewonly=True,
    )

    __table_args__ = (
        Index("idx_facility_city", "city"),
        {"extend_existing": True},
    )
