import argparse
import time
from pathlib import Path

import cv2
import numpy as np
import torch

from core.constants.waste import DETECTION_CLASS_NAME
from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from modules.classification.services.object_detector.service import ObjectDetector
from modules.classification.services.temporal_smoother.service import compute_iou
from training.common import (
    DETECTION_DIR,
    DETECTOR_WEIGHTS,
    IMAGE_EXTENSIONS,
    MULTI_OBJECT_TEST_DIR,
    write_json_report,
)

IOU_MATCH_THRESHOLD = 0.5


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluasi YOLO26")
    parser.add_argument("--data", default=str(DETECTION_DIR / "data.yaml"))
    parser.add_argument("--weights", default=str(DETECTOR_WEIGHTS))
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default="0")
    parser.add_argument("--multi-object", action="store_true")
    parser.add_argument(
        "--test-images-have-clahe",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Citra data/detection sudah melalui CLAHE (bawaan build_detection_dataset).",
    )
    options = parser.parse_args()

    from ultralytics import YOLO

    metrics = YOLO(options.weights).val(
        data=options.data,
        split="test",
        imgsz=options.imgsz,
        batch=options.batch,
        device=options.device,
        project=str(Path(options.weights).parent.parent / "detector_runs"),
        name="test_eval",
        exist_ok=True,
    )

    detector = ObjectDetector(weights_path=options.weights)
    results = {
        "weights": options.weights,
        "class": DETECTION_CLASS_NAME,
        "test_ultralytics": {
            "precision": float(metrics.box.mp),
            "recall": float(metrics.box.mr),
            "map50": float(metrics.box.map50),
            "map50_95": float(metrics.box.map),
        },
        "test_production_threshold": evaluate_folder(
            detector,
            DETECTION_DIR / "images" / "test",
            DETECTION_DIR / "labels" / "test",
            apply_clahe=not options.test_images_have_clahe,
        ),
    }

    if options.multi_object:
        results["multi_object_test"] = evaluate_folder(
            detector,
            MULTI_OBJECT_TEST_DIR / "images",
            MULTI_OBJECT_TEST_DIR / "labels",
            apply_clahe=True,
        )

    report = write_json_report("detector_evaluation.json", results)
    print(f"Laporan: {report}")


def evaluate_folder(
    detector: ObjectDetector,
    images_dir: Path,
    labels_dir: Path,
    apply_clahe: bool,
) -> dict:
    preprocessor = ImagePreprocessor() if apply_clahe else None
    image_paths = sorted(
        p for p in images_dir.glob("*") if p.suffix.lower() in IMAGE_EXTENSIONS
    )
    true_positive = false_positive = false_negative = 0
    matched_ious: list[float] = []
    timings_ms: list[float] = []

    for image_path in image_paths:
        bgr = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        height, width = rgb.shape[:2]
        ground_truth = read_ground_truth(
            labels_dir / f"{image_path.stem}.txt", width, height
        )

        started_at = time.perf_counter()
        frame = preprocessor.process(rgb) if preprocessor else rgb
        predictions = detector.detect(frame)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        timings_ms.append((time.perf_counter() - started_at) * 1000)

        used: set[int] = set()
        for prediction in predictions:
            box = np.array([prediction.x1, prediction.y1, prediction.x2, prediction.y2])
            best_iou, best_index = 0.0, -1
            for index, truth in enumerate(ground_truth):
                if index in used:
                    continue
                overlap = compute_iou(box, truth)
                if overlap > best_iou:
                    best_iou, best_index = overlap, index
            if best_iou >= IOU_MATCH_THRESHOLD:
                used.add(best_index)
                true_positive += 1
                matched_ious.append(best_iou)
            else:
                false_positive += 1
        false_negative += len(ground_truth) - len(used)

    precision = true_positive / max(true_positive + false_positive, 1)
    recall = true_positive / max(true_positive + false_negative, 1)
    return {
        "images": len(image_paths),
        "confidence_threshold": detector.confidence_threshold,
        "iou_match_threshold": IOU_MATCH_THRESHOLD,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / max(precision + recall, 1e-12),
        "mean_iou_matched": float(np.mean(matched_ious)) if matched_ious else None,
        "ms_per_image": {
            "mean": float(np.mean(timings_ms)) if timings_ms else None,
            "median": float(np.median(timings_ms)) if timings_ms else None,
        },
    }


def read_ground_truth(label_path: Path, width: int, height: int) -> list[np.ndarray]:
    if not label_path.exists():
        return []
    boxes = []
    for line in label_path.read_text(encoding="utf-8").splitlines():
        values = line.split()
        if len(values) != 5:
            continue
        cx, cy, w, h = (float(v) for v in values[1:])
        boxes.append(
            np.array(
                [
                    (cx - w / 2) * width,
                    (cy - h / 2) * height,
                    (cx + w / 2) * width,
                    (cy + h / 2) * height,
                ]
            )
        )
    return boxes


if __name__ == "__main__":
    main()
