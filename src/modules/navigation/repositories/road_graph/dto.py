from typing import NamedTuple

from pydantic import BaseModel, Field, model_validator


class DBoundingBox(BaseModel):
    min_latitude: float = Field(ge=-90, le=90)
    min_longitude: float = Field(ge=-180, le=180)
    max_latitude: float = Field(ge=-90, le=90)
    max_longitude: float = Field(ge=-180, le=180)

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.min_latitude > self.max_latitude:
            raise ValueError("min_latitude must be <= max_latitude")
        if self.min_longitude > self.max_longitude:
            raise ValueError("min_longitude must be <= max_longitude")
        return self

    @classmethod
    def from_points(
        cls,
        points: list[tuple[float, float]],
        padding_degree: float = 0.0,
    ) -> "DBoundingBox":
        latitudes = [lat for lat, _ in points]
        longitudes = [lon for _, lon in points]
        return cls(
            min_latitude=min(latitudes) - padding_degree,
            min_longitude=min(longitudes) - padding_degree,
            max_latitude=max(latitudes) + padding_degree,
            max_longitude=max(longitudes) + padding_degree,
        )


class DRoadEdgeRow(NamedTuple):
    from_node_id: int
    to_node_id: int
    distance_meter: float
    from_latitude: float
    from_longitude: float
    to_latitude: float
    to_longitude: float
