from sqlalchemy import BigInteger, Float, String, Integer, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
from infrastructures.persistence.model.base import AbstractModel

class MOSMNode(AbstractModel):
    __tablename__ = "osm_nodes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    network_type: Mapped[str] = mapped_column(String(20), primary_key=True)

    __table_args__ = (
        Index("idx_osm_nodes_lat_lon", "lat", "lon"),
        {"extend_existing": True}
    )

class MOSMEdge(AbstractModel):
    __tablename__ = "osm_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    u: Mapped[int] = mapped_column(BigInteger, nullable=False)
    v: Mapped[int] = mapped_column(BigInteger, nullable=False)
    key: Mapped[int] = mapped_column(Integer, default=0)
    network_type: Mapped[str] = mapped_column(String(20), nullable=False)
    length: Mapped[float] = mapped_column(Float, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    highway: Mapped[str | None] = mapped_column(String(50), nullable=True)
    oneway: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    geometry_wkt: Mapped[str | None] = mapped_column(String, nullable=True)
    maxspeed: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("idx_osm_edges_u_network", "u", "network_type"),
        Index("idx_osm_edges_v_network", "v", "network_type"),
        {"extend_existing": True}
    )
