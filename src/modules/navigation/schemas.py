from pydantic import BaseModel, Field

class SRouteRequest(BaseModel):
    start_lat: float = Field(..., description="Latitude awal", example=-6.169737)
    start_lon: float = Field(..., description="Longitude awal", example=106.788864)
    end_lat: float = Field(..., description="Latitude akhir", example=-6.170068)
    end_lon: float = Field(..., description="Longitude akhir", example=106.787616)
    mode: str = Field("walk", description="Mode perjalanan: walk atau drive", example="walk")

from typing import List

class SNavigationResponse(BaseModel):
    mode: str
    distance_meters: float
    start_node_id: int
    goal_node_id: int
    route: List[List[float]]

