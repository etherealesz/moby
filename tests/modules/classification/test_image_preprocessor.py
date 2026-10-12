import cv2
import numpy as np
import pytest

from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from tests.modules.classification import manual_color


@pytest.fixture
def image() -> np.ndarray:
    rng = np.random.default_rng(0)
    noise = rng.integers(0, 256, size=(120, 160, 3), dtype=np.uint8)
    gradient = np.linspace(0, 255, 160, dtype=np.uint8)[None, :, None]
    return np.where(rng.random((120, 160, 1)) < 0.5, noise, gradient).astype(np.uint8)


def test_rgb_to_lab_matches_manual_equations(image: np.ndarray):
    preprocessor = ImagePreprocessor()

    opencv_lab = preprocessor.rgb_to_lab(image).astype(int)
    manual_lab = manual_color.lab_to_opencv_8bit(manual_color.rgb_to_lab(image)).astype(
        int
    )

    diff = np.abs(opencv_lab - manual_lab)
    assert diff.max() <= 2
    assert diff.mean() < 0.5


def test_lab_to_rgb_matches_manual_equations(image: np.ndarray):
    preprocessor = ImagePreprocessor()
    lab_uint8 = preprocessor.rgb_to_lab(image)

    opencv_rgb = preprocessor.lab_to_rgb(lab_uint8).astype(int)
    manual_rgb = manual_color.lab_to_rgb(
        manual_color.opencv_8bit_to_lab(lab_uint8)
    ).astype(int)

    diff = np.abs(opencv_rgb - manual_rgb)
    assert diff.max() <= 3
    assert diff.mean() < 0.5


def test_process_is_composition_of_steps(image: np.ndarray):
    preprocessor = ImagePreprocessor(clip_limit=2.0, tile_grid_size=(8, 8))

    lab = preprocessor.rgb_to_lab(image)
    lightness, a_channel, b_channel = cv2.split(lab)
    expected = preprocessor.lab_to_rgb(
        cv2.merge((preprocessor.apply_clahe(lightness), a_channel, b_channel))
    )

    assert np.array_equal(preprocessor.process(image), expected)


def test_clahe_matches_opencv_reference(image: np.ndarray):
    preprocessor = ImagePreprocessor(clip_limit=1.5, tile_grid_size=(2, 2))
    lightness = preprocessor.rgb_to_lab(image)[..., 0].copy()

    reference = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(2, 2)).apply(lightness)

    assert np.array_equal(preprocessor.apply_clahe(lightness), reference)


def test_clahe_only_changes_lightness_channel(image: np.ndarray):
    preprocessor = ImagePreprocessor()
    lab = preprocessor.rgb_to_lab(image)
    lightness, a_channel, b_channel = cv2.split(lab)

    enhanced = cv2.merge((preprocessor.apply_clahe(lightness), a_channel, b_channel))

    assert np.array_equal(enhanced[..., 1], lab[..., 1])
    assert np.array_equal(enhanced[..., 2], lab[..., 2])
    assert not np.array_equal(enhanced[..., 0], lab[..., 0])


def test_process_increases_contrast_of_low_contrast_image():
    rng = np.random.default_rng(1)
    dull = rng.integers(100, 130, size=(128, 128, 3), dtype=np.uint8)

    enhanced = ImagePreprocessor(clip_limit=2.0, tile_grid_size=(8, 8)).process(dull)

    lightness_before = cv2.cvtColor(dull, cv2.COLOR_RGB2LAB)[..., 0].std()
    lightness_after = cv2.cvtColor(enhanced, cv2.COLOR_RGB2LAB)[..., 0].std()
    assert enhanced.shape == dull.shape
    assert enhanced.dtype == np.uint8
    assert lightness_after > lightness_before


def test_process_rejects_non_rgb_input():
    with pytest.raises(ValueError):
        ImagePreprocessor().process(np.zeros((10, 10), dtype=np.uint8))
