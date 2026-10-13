from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, ForeignKey, Identity, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructures.persistence.model.base import AbstractModel


class RoadEdge(AbstractModel):
    """
    Tabel Road_Edge (Tabel L9.6) ditambah kolom network_type dan oneway
    (Keputusan Terbuka nomor 1, lihat docs/keputusan.md).

    Setiap baris adalah sisi berarah from_node_id -> to_node_id. Jalan dua arah
    disimpan sebagai dua baris.
    """

    __tablename__ = "road_edge"

    edge_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    from_node_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("road_node.node_id"), nullable=False
    )
    to_node_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("road_node.node_id"), nullable=False
    )
    distance_meter: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    network_type: Mapped[str] = mapped_column(String(10), nullable=False)
    oneway: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("idx_road_edge_network_type_from_node", "network_type", "from_node_id"),
        Index("idx_road_edge_to_node", "to_node_id"),
        {"extend_existing": True},
    )
