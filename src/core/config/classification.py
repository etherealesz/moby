from pydantic import BaseModel, Field


class ClaheConfig(BaseModel):
    clip_limit: float = Field(alias="clipLimit", default=2.0, gt=0)
    tile_grid_size: tuple[int, int] = Field(alias="tileGridSize", default=(8, 8))


class DetectorConfig(BaseModel):
    weights_path: str = Field(alias="weightsPath", default="models/detector/best.pt")
    confidence_threshold: float = Field(
        alias="confidenceThreshold", default=0.5, ge=0, le=1
    )
    image_size: int = Field(alias="imageSize", default=640, gt=0)


class ClassifierConfig(BaseModel):
    weights_path: str = Field(alias="weightsPath", default="models/classifier/best.pt")
    image_size: int = Field(alias="imageSize", default=224, gt=0)


class TemporalSmoothingConfig(BaseModel):
    alpha: float = Field(default=0.6, gt=0, le=1)
    beta: float = Field(default=0.5, gt=0, le=1)
    margin: float = Field(default=0.15, ge=0, le=1)
    n_frames: int = Field(alias="nFrames", default=3, ge=1)
    iou_threshold: float = Field(alias="iouThreshold", default=0.3, ge=0, le=1)
    max_missed_frames: int = Field(alias="maxMissedFrames", default=5, ge=0)


class ClassificationConfig(BaseModel):
    device: str = Field(default="auto")
    clahe: ClaheConfig = Field(default=ClaheConfig())
    detector: DetectorConfig = Field(default=DetectorConfig())
    classifier: ClassifierConfig = Field(default=ClassifierConfig())
    temporal_smoothing: TemporalSmoothingConfig = Field(
        alias="temporalSmoothing", default=TemporalSmoothingConfig()
    )
