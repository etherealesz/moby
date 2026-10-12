from dataclasses import dataclass

import numpy as np


@dataclass
class DTrack:
    track_id: int
    box: np.ndarray
    probabilities: np.ndarray
    detection_confidence: float
    label_index: int
    candidate_index: int | None = None
    candidate_frames: int = 0
    missed_frames: int = 0


@dataclass(frozen=True)
class DSmoothedObject:
    track_id: int
    box: tuple[float, float, float, float]
    detection_confidence: float
    probabilities: tuple[float, ...]
    label_index: int
