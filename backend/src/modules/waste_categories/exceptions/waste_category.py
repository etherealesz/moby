from core.exceptions.base import ApplicationError


class GetWasteCategoryFailedError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("GET_WASTE_CATEGORY_FAILED")
