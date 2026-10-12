from pydantic import BaseModel, Field


class NavigationConfig(BaseModel):
    max_candidate_facilities: int = Field(alias="maxCandidateFacilities", default=5, ge=1)
    max_search_radius_meter: float = Field(
        alias="maxSearchRadiusMeter", default=20_000, gt=0
    )
    bbox_padding_degree: float = Field(alias="bboxPaddingDegree", default=0.01, ge=0)
    max_snap_distance_meter: float = Field(
        alias="maxSnapDistanceMeter", default=1_000, gt=0
    )
