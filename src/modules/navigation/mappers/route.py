from modules.facilities.mappers.facility import map_facility_to_response
from modules.navigation.schemas.route import SCandidateRouteResponse, SRouteResponse
from modules.navigation.services.navigation_service.dto import DRouteResult


def map_route_result_to_response(result: DRouteResult) -> SRouteResponse:
    return SRouteResponse(
        facility=map_facility_to_response(result.facility),
        network_type=result.network_type,
        route=result.route,
        distance_meter=round(result.distance_meter, 2),
        explored_nodes=result.explored_nodes,
        computation_time_ms=round(result.computation_time_ms, 3),
        graph_load_time_ms=round(result.graph_load_time_ms, 3),
        graph_node_count=result.graph_node_count,
        graph_edge_count=result.graph_edge_count,
        candidates=[
            SCandidateRouteResponse(
                facility_id=candidate.facility_id,
                straight_distance_meter=round(candidate.straight_distance_meter, 2),
                route_distance_meter=(
                    round(candidate.route_distance_meter, 2)
                    if candidate.route_distance_meter is not None
                    else None
                ),
                explored_nodes=candidate.explored_nodes,
                computation_time_ms=round(candidate.computation_time_ms, 3),
            )
            for candidate in result.candidates
        ],
    )
