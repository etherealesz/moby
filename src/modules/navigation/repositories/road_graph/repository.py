from injector import inject
from sqlalchemy import Float, cast, select
from sqlalchemy.orm import aliased

from core.enums.network_type import ENetworkType
from core.logger.factory import create_app_logger
from infrastructures.databases.master import DatabaseMasterSession
from modules.navigation.exceptions.navigation import GetRoadGraphFailedError
from modules.navigation.models.road_edge import RoadEdge
from modules.navigation.models.road_node import RoadNode
from modules.navigation.repositories.road_graph.dto import DBoundingBox, DRoadEdgeRow

logger = create_app_logger()


class IRoadGraphRepository:
    @inject
    def __init__(self, session: DatabaseMasterSession) -> None:
        self._session = session

    async def get_edges_in_bbox(
        self,
        network_type: ENetworkType,
        bbox: DBoundingBox,
    ) -> list[DRoadEdgeRow]:
        logger.info("Executing get_edges_in_bbox method in IRoadGraphRepository")

        from_node = aliased(RoadNode)
        to_node = aliased(RoadNode)

        stmt = (
            select(
                RoadEdge.from_node_id,
                RoadEdge.to_node_id,
                cast(RoadEdge.distance_meter, Float).label("distance_meter"),
                cast(from_node.latitude, Float).label("from_latitude"),
                cast(from_node.longitude, Float).label("from_longitude"),
                cast(to_node.latitude, Float).label("to_latitude"),
                cast(to_node.longitude, Float).label("to_longitude"),
            )
            .join(from_node, from_node.node_id == RoadEdge.from_node_id)
            .join(to_node, to_node.node_id == RoadEdge.to_node_id)
            .where(
                RoadEdge.network_type == network_type.value,
                from_node.latitude.between(bbox.min_latitude, bbox.max_latitude),
                from_node.longitude.between(bbox.min_longitude, bbox.max_longitude),
                to_node.latitude.between(bbox.min_latitude, bbox.max_latitude),
                to_node.longitude.between(bbox.min_longitude, bbox.max_longitude),
            )
        )

        try:
            res = await self._session.execute(stmt)
        except Exception as exc:
            logger.exception("Error occurred while fetching road graph", exc_info=True)
            raise GetRoadGraphFailedError from exc

        return [DRoadEdgeRow(*row) for row in res.all()]
