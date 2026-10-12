from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1c3e5f7b9d2"
down_revision: Union[str, Sequence[str], None] = "74364a1d6009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "waste_category",
        sa.Column("category_id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("category_name", sa.String(length=50), nullable=False),
        sa.Column("category_code", sa.String(length=10), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("category_id"),
    )
    op.create_table(
        "waste_subcategory",
        sa.Column("subcategory_id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("subcategory_name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["category_id"], ["waste_category.category_id"]),
        sa.PrimaryKeyConstraint("subcategory_id"),
    )
    op.create_table(
        "facility",
        sa.Column("facility_id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("facility_name", sa.String(length=100), nullable=False),
        sa.Column("facility_type", sa.String(length=20), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column("address", sa.String(length=200), nullable=True),
        sa.Column("city", sa.String(length=50), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("facility_id"),
    )
    op.create_index("idx_facility_city", "facility", ["city"], unique=False)
    op.create_table(
        "facility_category",
        sa.Column("facility_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["category_id"], ["waste_category.category_id"]),
        sa.ForeignKeyConstraint(["facility_id"], ["facility.facility_id"]),
        sa.PrimaryKeyConstraint("facility_id", "category_id"),
    )
    op.create_table(
        "road_node",
        sa.Column("node_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.PrimaryKeyConstraint("node_id"),
    )
    op.create_index(
        "idx_road_node_latitude_longitude",
        "road_node",
        ["latitude", "longitude"],
        unique=False,
    )
    op.create_table(
        "road_edge",
        sa.Column("edge_id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("from_node_id", sa.BigInteger(), nullable=False),
        sa.Column("to_node_id", sa.BigInteger(), nullable=False),
        sa.Column("distance_meter", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("network_type", sa.String(length=10), nullable=False),
        sa.Column("oneway", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["from_node_id"], ["road_node.node_id"]),
        sa.ForeignKeyConstraint(["to_node_id"], ["road_node.node_id"]),
        sa.PrimaryKeyConstraint("edge_id"),
    )

    op.execute(
        """
        INSERT INTO road_node (node_id, latitude, longitude)
        SELECT DISTINCT ON (id) id, ROUND(lat::numeric, 7), ROUND(lon::numeric, 7)
        FROM osm_nodes
        ORDER BY id
        """
    )
    op.execute(
        """
        INSERT INTO road_edge (from_node_id, to_node_id, distance_meter, network_type, oneway)
        SELECT e.u, e.v, ROUND(MIN(e.length)::numeric, 2), e.network_type,
               BOOL_OR(COALESCE(e.oneway, false))
        FROM osm_edges e
        WHERE EXISTS (SELECT 1 FROM road_node n WHERE n.node_id = e.u)
          AND EXISTS (SELECT 1 FROM road_node n WHERE n.node_id = e.v)
        GROUP BY e.u, e.v, e.network_type
        """
    )

    op.create_index(
        "idx_road_edge_network_type_from_node",
        "road_edge",
        ["network_type", "from_node_id"],
        unique=False,
    )
    op.create_index("idx_road_edge_to_node", "road_edge", ["to_node_id"], unique=False)

    op.drop_index("idx_osm_edges_u_network", table_name="osm_edges")
    op.drop_index("idx_osm_edges_v_network", table_name="osm_edges")
    op.drop_table("osm_edges")
    op.drop_index("idx_osm_nodes_lat_lon", table_name="osm_nodes")
    op.drop_table("osm_nodes")
    op.drop_table("posts")


def downgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("views", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "osm_nodes",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("network_type", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id", "network_type"),
    )
    op.create_index("idx_osm_nodes_lat_lon", "osm_nodes", ["lat", "lon"], unique=False)
    op.create_table(
        "osm_edges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("u", sa.BigInteger(), nullable=False),
        sa.Column("v", sa.BigInteger(), nullable=False),
        sa.Column("key", sa.Integer(), nullable=False),
        sa.Column("network_type", sa.String(length=20), nullable=False),
        sa.Column("length", sa.Float(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("highway", sa.String(length=50), nullable=True),
        sa.Column("oneway", sa.Boolean(), nullable=True),
        sa.Column("geometry_wkt", sa.String(), nullable=True),
        sa.Column("maxspeed", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_osm_edges_u_network", "osm_edges", ["u", "network_type"], unique=False
    )
    op.create_index(
        "idx_osm_edges_v_network", "osm_edges", ["v", "network_type"], unique=False
    )

    op.execute(
        """
        INSERT INTO osm_nodes (id, lat, lon, network_type)
        SELECT DISTINCT n.node_id, n.latitude::float8, n.longitude::float8, e.network_type
        FROM road_node n
        JOIN road_edge e ON e.from_node_id = n.node_id OR e.to_node_id = n.node_id
        """
    )
    op.execute(
        """
        INSERT INTO osm_edges (u, v, key, network_type, length, oneway)
        SELECT from_node_id, to_node_id, 0, network_type, distance_meter::float8, oneway
        FROM road_edge
        """
    )

    op.drop_index("idx_road_edge_to_node", table_name="road_edge")
    op.drop_index("idx_road_edge_network_type_from_node", table_name="road_edge")
    op.drop_table("road_edge")
    op.drop_index("idx_road_node_latitude_longitude", table_name="road_node")
    op.drop_table("road_node")
    op.drop_table("facility_category")
    op.drop_index("idx_facility_city", table_name="facility")
    op.drop_table("facility")
    op.drop_table("waste_subcategory")
    op.drop_table("waste_category")
