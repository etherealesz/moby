from pydantic import BaseModel, Field


class SFacilityResponse(BaseModel):
    facility_id: int
    facility_name: str
    facility_type: str
    latitude: float
    longitude: float
    address: str | None
    city: str
    categories: list[str] | None = Field(
        exclude_if=lambda categories: categories is None,
        default=None,
    )
