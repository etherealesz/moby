from typing import Tuple, overload

from core.dtos.pagination import DPagination


@overload
def build_limit_offset(page: int, page_size: int, /) -> Tuple[int, int]: ...


@overload
def build_limit_offset(dto: DPagination, /) -> Tuple[int, int]: ...


def build_limit_offset(
    page: int | DPagination,
    page_size: int | None = None,
    /,
) -> Tuple[int, int]:
    if isinstance(page, DPagination):
        page_size = page.items_per_page
        page = page.page

    if page_size is None:
        raise ValueError("page_size must be provided when page is an int")

    limit = page_size
    offset = (page - 1) * page_size
    return limit, offset
