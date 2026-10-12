from app.schemas.request import SOptionalPagination, SPagination
from core.constants.pagination import DEFAULT_PAGINATION_SIZE
from core.dtos.pagination import DPagination


def map_pagination_schema_to_pagination_dto(schema: SPagination) -> DPagination:
    return DPagination(page=schema.page, items_per_page=schema.page_size)


def map_optional_pagination_schema_to_pagination_dto(
    schema: SOptionalPagination,
) -> DPagination | None:
    if schema.page and not schema.page_size:
        schema.page_size = DEFAULT_PAGINATION_SIZE
    if not schema.page and schema.page_size:
        schema.page = 1

    if schema.page and schema.page_size:
        return DPagination(page=schema.page, items_per_page=schema.page_size)
    return None
