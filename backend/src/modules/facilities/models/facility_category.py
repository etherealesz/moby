from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from infrastructures.persistence.model.base import AbstractModel
from infrastructures.persistence.model.mixin import TimestampMixin


class FacilityCategory(AbstractModel, TimestampMixin):
    """Tabel Facility_Category (Lampiran 9): kategori sampah yang diterima fasilitas."""

    __tablename__ = "facility_category"

    facility_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("facility.facility_id"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("waste_category.category_id"), primary_key=True
    )
