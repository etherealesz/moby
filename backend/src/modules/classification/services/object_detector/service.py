import threading
from pathlib import Path

import numpy as np
from ultralytics import YOLO

from core.config.settings import settings
from core.constants.paths import PROJECT_ROOT
from core.logger.factory import create_app_logger
from core.utils.device_helper import resolve_torch_device
from modules.classification.exceptions.classification import (
    DetectorModelNotAvailableError,
)
from modules.classification.services.object_detector.dto import DBox

logger = create_app_logger()


class ObjectDetector:
    def __init__(
        self,
        weights_path: str | Path | None = None,
        confidence_threshold: float | None = None,
    ) -> None:
        detector_config = settings.classification.detector
        self._weights_path = _resolve_path(weights_path or detector_config.weights_path)
        self._confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else detector_config.confidence_threshold
        )
        self._image_size = detector_config.image_size
        self._device = resolve_torch_device(settings.classification.device)
        self._model = None
        self._lock = threading.Lock()

    @property
    def confidence_threshold(self) -> float:
        return self._confidence_threshold

    def _load_model(self):
        if self._model is not None:
            return self._model

        if not self._weights_path.exists():
            logger.error(f"Detector weights not found: {self._weights_path}")
            raise DetectorModelNotAvailableError

        logger.info(f"Loading detector weights from {self._weights_path}")
        self._model = YOLO(str(self._weights_path))
        return self._model

    def detect(self, frame: np.ndarray) -> list[DBox]:
        with self._lock:
            model = self._load_model()
            results = model.predict(
                source=np.ascontiguousarray(frame[..., ::-1]),
                conf=self._confidence_threshold,
                imgsz=self._image_size,
                device=self._device,
                quantize=16 if self._device.startswith("cuda") else None,
                verbose=False,
            )

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return []

        xyxy = boxes.xyxy.cpu().numpy()
        confidences = boxes.conf.cpu().numpy()
        detections = [
            DBox(
                x1=float(x1),
                y1=float(y1),
                x2=float(x2),
                y2=float(y2),
                confidence=float(confidence),
            )
            for (x1, y1, x2, y2), confidence in zip(xyxy, confidences)
            if confidence >= self._confidence_threshold
        ]
        detections.sort(key=lambda box: box.confidence, reverse=True)
        return detections

    def crop(self, frame: np.ndarray, boxes: list[DBox]) -> list[np.ndarray]:
        height, width = frame.shape[:2]
        crops: list[np.ndarray] = []
        for box in boxes:
            x1 = int(np.clip(np.floor(box.x1), 0, width - 1))
            y1 = int(np.clip(np.floor(box.y1), 0, height - 1))
            x2 = int(np.clip(np.ceil(box.x2), x1 + 1, width))
            y2 = int(np.clip(np.ceil(box.y2), y1 + 1, height))
            crops.append(frame[y1:y2, x1:x2])
        return crops


def _resolve_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path
