import math

from pydantic import BaseModel, Field, computed_field

from core.constants.pagination import DEFAULT_PAGINATION_SIZE


class DPagination(BaseModel):
    page: int = Field(default=1)
    items_per_page: int = Field(default=DEFAULT_PAGINATION_SIZE)


class DPaginationMeta(BaseModel):
    total_items: int
    current_page: int
    items_per_page: int

    @computed_field
    @property
    def total_pages(self) -> int:
        if self.items_per_page <= 0:
            return 0
        return math.ceil(self.total_items / self.items_per_page)

    @computed_field
    @property
    def has_next_page(self) -> bool:
        return self.current_page < self.total_pages

    @computed_field
    @property
    def has_previous_page(self) -> bool:
        return self.current_page > 1
