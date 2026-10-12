import asyncio
import time

import cv2
import numpy as np
from injector import inject

from core.constants.waste import WASTE_CATEGORY_LABELS
from core.logger.factory import create_app_logger
from modules.classification.exceptions.classification import InvalidImageError
from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from modules.classification.services.object_detector.service import ObjectDetector
from modules.classification.services.temporal_smoother.service import TemporalSmoother
from modules.classification.services.waste_classifier.service import WasteClassifier
from modules.classification.use_cases.classify_frame.dto import (
    DClassifiedObject,
    DClassifyFrameResult,
)

logger = create_app_logger()


class ClassifyFrameUseCase:
    @inject
    def __init__(
        self,
        image_preprocessor: ImagePreprocessor,
        object_detector: ObjectDetector,
        waste_classifier: WasteClassifier,
    ) -> None:
        self._image_preprocessor = image_preprocessor
        self._object_detector = object_detector
        self._waste_classifier = waste_classifier

    async def execute(
        self,
        image_bytes: bytes,
        smoother: TemporalSmoother | None = None,
    ) -> DClassifyFrameResult:
        logger.info("Executing ClassifyFrameUseCase")

        return await asyncio.to_thread(self._run, image_bytes, smoother)

    def _run(
        self,
        image_bytes: bytes,
        smoother: TemporalSmoother | None,
    ) -> DClassifyFrameResult:
        started_at = time.perf_counter()
        frame = _decode_image(image_bytes)
        height, width = frame.shape[:2]

        enhanced = self._image_preprocessor.process(frame)
        preprocessed_at = time.perf_counter()

        boxes = self._object_detector.detect(enhanced)
        crops = self._object_detector.crop(enhanced, boxes)
        detected_at = time.perf_counter()

        classifications = self._waste_classifier.predict(crops)
        classified_at = time.perf_counter()

        if smoother is not None:
            smoothed = smoother.update(
                boxes,
                [classification.probabilities for classification in classifications],
            )
            objects = [
                _build_object(
                    track_id=item.track_id,
                    box=item.box,
                    detection_confidence=item.detection_confidence,
                    probabilities=item.probabilities,
                    label_index=item.label_index,
                )
                for item in smoothed
            ]
        else:
            objects = [
                _build_object(
                    track_id=None,
                    box=(box.x1, box.y1, box.x2, box.y2),
                    detection_confidence=box.confidence,
                    probabilities=tuple(classification.probabilities.tolist()),
                    label_index=WASTE_CATEGORY_LABELS.index(classification.label),
                )
                for box, classification in zip(boxes, classifications)
            ]

        finished_at = time.perf_counter()
        return DClassifyFrameResult(
            width=width,
            height=height,
            objects=objects,
            preprocess_time_ms=(preprocessed_at - started_at) * 1000,
            detection_time_ms=(detected_at - preprocessed_at) * 1000,
            classification_time_ms=(classified_at - detected_at) * 1000,
            total_time_ms=(finished_at - started_at) * 1000,
        )


def _decode_image(image_bytes: bytes) -> np.ndarray:
    if not image_bytes:
        raise InvalidImageError

    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    bgr = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if bgr is None:
        raise InvalidImageError
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def _build_object(
    track_id: int | None,
    box: tuple[float, float, float, float],
    detection_confidence: float,
    probabilities: tuple[float, ...],
    label_index: int,
) -> DClassifiedObject:
    return DClassifiedObject(
        track_id=track_id,
        x1=box[0],
        y1=box[1],
        x2=box[2],
        y2=box[3],
        detection_confidence=detection_confidence,
        label=WASTE_CATEGORY_LABELS[label_index],
        confidence=probabilities[label_index],
        probabilities=dict(zip(WASTE_CATEGORY_LABELS, probabilities)),
    )
