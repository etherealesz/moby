import numpy as np
import pytest

from modules.classification.services.object_detector.dto import DBox
from modules.classification.services.temporal_smoother.service import (
    TemporalSmoother,
    compute_iou,
)

ANORGANIK = np.array([0.7, 0.1, 0.1, 0.1])
ORGANIK = np.array([0.05, 0.05, 0.85, 0.05])


def box(x1: float, y1: float, x2: float, y2: float, confidence: float = 0.9) -> DBox:
    return DBox(x1, y1, x2, y2, confidence)


def test_compute_iou():
    assert compute_iou(np.array([0, 0, 10, 10]), np.array([0, 0, 10, 10])) == 1.0
    assert compute_iou(np.array([0, 0, 10, 10]), np.array([20, 20, 30, 30])) == 0.0
    assert compute_iou(
        np.array([0, 0, 10, 10]), np.array([5, 0, 15, 10])
    ) == pytest.approx(50 / 150)


def test_box_and_probability_smoothing_follow_equations():
    smoother = TemporalSmoother(alpha=0.6, beta=0.5, margin=0.15, n_frames=3)
    smoother.update([box(0, 0, 100, 100)], [ANORGANIK])
    second = smoother.update([box(10, 10, 110, 110)], [ORGANIK])[0]

    assert second.box == pytest.approx((6.0, 6.0, 106.0, 106.0))
    assert np.array(second.probabilities) == pytest.approx(
        0.5 * ORGANIK + 0.5 * ANORGANIK
    )
    assert second.track_id == 1


def test_hysteresis_keeps_label_until_n_frames():
    smoother = TemporalSmoother(alpha=1.0, beta=0.9, margin=0.15, n_frames=3)
    first = smoother.update([box(0, 0, 100, 100)], [ANORGANIK])[0]
    assert first.label_index == 0

    labels = [
        smoother.update([box(0, 0, 100, 100)], [ORGANIK])[0].label_index for _ in range(3)
    ]
    assert labels == [0, 0, 2]


def test_small_lead_does_not_switch_label():
    smoother = TemporalSmoother(alpha=1.0, beta=1.0, margin=0.15, n_frames=1)
    smoother.update([box(0, 0, 100, 100)], [np.array([0.5, 0.0, 0.4, 0.1])])
    result = smoother.update([box(0, 0, 100, 100)], [np.array([0.42, 0.0, 0.48, 0.1])])[0]
    assert result.label_index == 0


def test_non_overlapping_detection_creates_new_track():
    smoother = TemporalSmoother(iou_threshold=0.3)
    smoother.update([box(0, 0, 50, 50)], [ANORGANIK])
    result = smoother.update(
        [box(0, 0, 50, 50), box(200, 200, 260, 260)], [ANORGANIK, ORGANIK]
    )

    assert [item.track_id for item in result] == [1, 2]
    assert result[1].label_index == 2


def test_lost_track_is_held_until_max_missed_frames():
    smoother = TemporalSmoother(max_missed_frames=1)
    smoother.update([box(0, 0, 50, 50)], [ANORGANIK])
    held = smoother.update([], [])
    assert [item.track_id for item in held] == [1]
    assert held[0].box == pytest.approx((0.0, 0.0, 50.0, 50.0))
    assert smoother.update([], []) == []
    result = smoother.update([box(0, 0, 50, 50)], [ANORGANIK])
    assert result[0].track_id == 2


def test_reset_clears_state():
    smoother = TemporalSmoother()
    smoother.update([box(0, 0, 50, 50)], [ANORGANIK])
    smoother.reset()
    assert smoother.update([box(0, 0, 50, 50)], [ANORGANIK])[0].track_id == 1
