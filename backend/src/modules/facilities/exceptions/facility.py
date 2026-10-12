from core.exceptions.base import ApplicationError


class GetFacilityFailedError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("GET_FACILITY_FAILED")
