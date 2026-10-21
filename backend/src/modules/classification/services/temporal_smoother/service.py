import numpy as np

from core.config.settings import settings
from modules.classification.services.object_detector.dto import DBox
from modules.classification.services.temporal_smoother.dto import (
    DSmoothedObject,
    DTrack,
)


class TemporalSmoother:
    def __init__(
        self,
        alpha: float | None = None,
        beta: float | None = None,
        margin: float | None = None,
        n_frames: int | None = None,
        iou_threshold: float | None = None,
        max_missed_frames: int | None = None,
    ) -> None:
        config = settings.classification.temporal_smoothing
        self.alpha = alpha if alpha is not None else config.alpha
        self.beta = beta if beta is not None else config.beta
        self.margin = margin if margin is not None else config.margin
        self.n_frames = n_frames if n_frames is not None else config.n_frames
        self.iou_threshold = (
            iou_threshold if iou_threshold is not None else config.iou_threshold
        )
        self.max_missed_frames = (
            max_missed_frames
            if max_missed_frames is not None
            else config.max_missed_frames
        )
        self._tracks: dict[int, DTrack] = {}
        self._next_track_id = 1

    def reset(self) -> None:
        self._tracks.clear()
        self._next_track_id = 1

    def update(
        self,
        boxes: list[DBox],
        probabilities: list[np.ndarray],
    ) -> list[DSmoothedObject]:
        if len(boxes) != len(probabilities):
            raise ValueError("boxes and probabilities must have the same length")

        assignments = self._match(boxes)
        matched_track_ids = set(assignments.values())

        outputs: list[DSmoothedObject] = []
        for index, (box, probs) in enumerate(zip(boxes, probabilities)):
            box_array = np.array([box.x1, box.y1, box.x2, box.y2], dtype=np.float64)
            probs_array = np.asarray(probs, dtype=np.float64)

            track_id = assignments.get(index)
            if track_id is None:
                track = self._create_track(box_array, probs_array, box.confidence)
                matched_track_ids.add(track.track_id)
            else:
                track = self._tracks[track_id]
                self._smooth(track, box_array, probs_array, box.confidence)

            outputs.append(_to_smoothed_object(track))

        for track_id in list(self._tracks):
            if track_id in matched_track_ids:
                continue
            track = self._tracks[track_id]
            track.missed_frames += 1
            if track.missed_frames > self.max_missed_frames:
                del self._tracks[track_id]
            else:
                outputs.append(_to_smoothed_object(track))

        return outputs

    def _match(self, boxes: list[DBox]) -> dict[int, int]:
        pairs: list[tuple[float, int, int]] = []
        for index, box in enumerate(boxes):
            current = np.array([box.x1, box.y1, box.x2, box.y2], dtype=np.float64)
            for track_id, track in self._tracks.items():
                overlap = compute_iou(current, track.box)
                if overlap >= self.iou_threshold:
                    pairs.append((overlap, index, track_id))

        pairs.sort(reverse=True)
        assignments: dict[int, int] = {}
        used_tracks: set[int] = set()
        for _, index, track_id in pairs:
            if index in assignments or track_id in used_tracks:
                continue
            assignments[index] = track_id
            used_tracks.add(track_id)
        return assignments

    def _create_track(
        self,
        box: np.ndarray,
        probabilities: np.ndarray,
        detection_confidence: float,
    ) -> DTrack:
        track = DTrack(
            track_id=self._next_track_id,
            box=box,
            probabilities=probabilities,
            detection_confidence=detection_confidence,
            label_index=int(np.argmax(probabilities)),
        )
        self._tracks[track.track_id] = track
        self._next_track_id += 1
        return track

    def _smooth(
        self,
        track: DTrack,
        box: np.ndarray,
        probabilities: np.ndarray,
        detection_confidence: float,
    ) -> None:
        track.box = self.alpha * box + (1.0 - self.alpha) * track.box
        track.probabilities = (
            self.beta * probabilities + (1.0 - self.beta) * track.probabilities
        )
        track.detection_confidence = (
            self.beta * detection_confidence
            + (1.0 - self.beta) * track.detection_confidence
        )
        track.missed_frames = 0
        self._apply_hysteresis(track)

    def _apply_hysteresis(self, track: DTrack) -> None:
        candidate = int(np.argmax(track.probabilities))
        lead = track.probabilities[candidate] - track.probabilities[track.label_index]

        if candidate == track.label_index or lead < self.margin:
            track.candidate_index = None
            track.candidate_frames = 0
            return

        if candidate == track.candidate_index:
            track.candidate_frames += 1
        else:
            track.candidate_index = candidate
            track.candidate_frames = 1

        if track.candidate_frames >= self.n_frames:
            track.label_index = candidate
            track.candidate_index = None
            track.candidate_frames = 0


def _to_smoothed_object(track: DTrack) -> DSmoothedObject:
    return DSmoothedObject(
        track_id=track.track_id,
        box=tuple(float(v) for v in track.box),
        detection_confidence=track.detection_confidence,
        probabilities=tuple(float(v) for v in track.probabilities),
        label_index=track.label_index,
    )


def compute_iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    inter_x1 = max(box_a[0], box_b[0])
    inter_y1 = max(box_a[1], box_b[1])
    inter_x2 = min(box_a[2], box_b[2])
    inter_y2 = min(box_a[3], box_b[3])
    intersection = max(0.0, inter_x2 - inter_x1) * max(0.0, inter_y2 - inter_y1)

    area_a = max(0.0, box_a[2] - box_a[0]) * max(0.0, box_a[3] - box_a[1])
    area_b = max(0.0, box_b[2] - box_b[0]) * max(0.0, box_b[3] - box_b[1])
    union = area_a + area_b - intersection
    return float(intersection / union) if union > 0 else 0.0
