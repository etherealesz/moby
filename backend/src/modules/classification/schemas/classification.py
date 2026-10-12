from pydantic import BaseModel


class SBoundingBoxResponse(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class SClassifiedObjectResponse(BaseModel):
    track_id: int | None
    box: SBoundingBoxResponse
    label: str
    confidence: float
    detection_confidence: float
    probabilities: dict[str, float]


class SClassifyFrameResponse(BaseModel):
    width: int
    height: int
    objects: list[SClassifiedObjectResponse]
    preprocess_time_ms: float
    detection_time_ms: float
    classification_time_ms: float
    total_time_ms: float
