from core.exceptions.base import ApplicationError


class GetRoadGraphFailedError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("GET_ROAD_GRAPH_FAILED")


class RoadGraphNotAvailableError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("ROAD_GRAPH_NOT_AVAILABLE")


class FacilityNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("FACILITY_NOT_FOUND")


class FacilityOutOfRangeError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("FACILITY_OUT_OF_RANGE")


class LocationOutOfCoverageError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("LOCATION_OUT_OF_COVERAGE")


class RouteNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("ROUTE_NOT_FOUND")
