from unittest.mock import MagicMock

import cv2
import numpy as np
import pytest

from modules.classification.exceptions.classification import InvalidImageError
from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from modules.classification.services.object_detector.dto import DBox
from modules.classification.services.object_detector.service import ObjectDetector
from modules.classification.services.temporal_smoother.service import TemporalSmoother
from modules.classification.services.waste_classifier.dto import DClassification
from modules.classification.use_cases.classify_frame.use_case import (
    ClassifyFrameUseCase,
)


def encode_jpeg(image_rgb: np.ndarray) -> bytes:
    ok, buffer = cv2.imencode(".jpg", cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
    assert ok
    return buffer.tobytes()


@pytest.fixture
def use_case() -> ClassifyFrameUseCase:
    detector = MagicMock(spec=ObjectDetector)
    detector.detect.return_value = [
        DBox(10, 20, 60, 90, 0.8),
        DBox(100, 40, 150, 100, 0.6),
    ]
    detector.crop.side_effect = ObjectDetector.crop.__get__(detector)

    classifier = MagicMock()
    classifier.predict.return_value = [
        DClassification(np.array([0.1, 0.7, 0.1, 0.1]), "B3"),
        DClassification(np.array([0.05, 0.05, 0.05, 0.85]), "Residu"),
    ]
    return ClassifyFrameUseCase(
        image_preprocessor=ImagePreprocessor(),
        object_detector=detector,
        waste_classifier=classifier,
    )


async def test_classify_single_frame(use_case: ClassifyFrameUseCase):
    image = np.random.default_rng(0).integers(0, 256, size=(120, 200, 3), dtype=np.uint8)

    result = await use_case.execute(encode_jpeg(image))

    assert (result.width, result.height) == (200, 120)
    assert [obj.label for obj in result.objects] == ["B3", "Residu"]
    assert result.objects[0].confidence == pytest.approx(0.7)
    assert result.objects[0].track_id is None
    assert set(result.objects[1].probabilities) == {
        "Anorganik",
        "B3",
        "Organik",
        "Residu",
    }
    crops = use_case._object_detector.crop.call_args.args[1]
    assert len(crops) == 2
    assert result.total_time_ms >= 0


async def test_classify_with_temporal_smoother(use_case: ClassifyFrameUseCase):
    image = np.zeros((120, 200, 3), dtype=np.uint8)
    smoother = TemporalSmoother()

    first = await use_case.execute(encode_jpeg(image), smoother)
    second = await use_case.execute(encode_jpeg(image), smoother)

    assert [obj.track_id for obj in first.objects] == [1, 2]
    assert [obj.track_id for obj in second.objects] == [1, 2]


async def test_invalid_image_raises(use_case: ClassifyFrameUseCase):
    with pytest.raises(InvalidImageError):
        await use_case.execute(b"bukan gambar")
