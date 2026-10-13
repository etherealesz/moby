from decimal import Decimal

from sqlalchemy import BigInteger, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from infrastructures.persistence.model.base import AbstractModel


class RoadNode(AbstractModel):
    """
    Tabel Road_Node (Tabel L9.5). node_id mengikuti osmid OSMnx dan dipakai
    bersama oleh jaringan walk dan drive (pembeda jaringan ada di Road_Edge).
    """

    __tablename__ = "road_node"

    node_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)

    __table_args__ = (
        Index("idx_road_node_latitude_longitude", "latitude", "longitude"),
        {"extend_existing": True},
    )
