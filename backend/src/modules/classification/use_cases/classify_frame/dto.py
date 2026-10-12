from pydantic import BaseModel


class DClassifiedObject(BaseModel):
    track_id: int | None
    x1: float
    y1: float
    x2: float
    y2: float
    detection_confidence: float
    label: str
    confidence: float
    probabilities: dict[str, float]


class DClassifyFrameResult(BaseModel):
    width: int
    height: int
    objects: list[DClassifiedObject]
    preprocess_time_ms: float
    detection_time_ms: float
    classification_time_ms: float
    total_time_ms: float
