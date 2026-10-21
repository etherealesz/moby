"""Evaluasi pipeline lengkap pada citra yang sama untuk dua pendekatan.

- dua-tahap  : CLAHE -> ObjectDetector (YOLO26 1 kelas) -> crop -> WasteClassifier (MobileNetV4)
- satu-tahap : CLAHE -> YOLO26 4 kelas (pembanding, tahap D)

Uji per citra (split val/test dataset klasifikasi): kelas citra = kelas kotak paling yakin;
citra tanpa deteksi dihitung salah ("tidak terdeteksi").
Uji per objek (opsional, --multi-object): data/multi_object_test/images + labels_4kelas
(format YOLO, id kelas 0-3 sesuai WASTE_CATEGORY_LABELS); objek benar bila IoU >= 0,5
dan kelasnya sama.
"""

import argparse
import time
from collections import Counter, defaultdict
from pathlib import Path
import cv2
import numpy as np
import torch
from tqdm import tqdm
from sklearn.metrics import precision_recall_fscore_support
from ultralytics import YOLO
from core.config.settings import settings
from core.constants.paths import PROJECT_ROOT
from core.constants.waste import WASTE_CATEGORY_LABELS
from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from modules.classification.services.object_detector.service import ObjectDetector
from modules.classification.services.temporal_smoother.service import compute_iou
from modules.classification.services.waste_classifier.service import WasteClassifier
from training.common import (
    IMAGE_EXTENSIONS,
    MANIFEST_CSV,
    MULTI_OBJECT_TEST_DIR,
    classifier_weights_path,
    detector_weights_path,
    log_experiment,
    read_manifest,
    write_csv_report,
    write_json_report,
)

IOU_MATCH_THRESHOLD = 0.5
MISSED = -1
MISSED_LABEL = "tidak terdeteksi"


class TwoStage:
    def __init__(self, detector_weights: str, classifier_weights: str) -> None:
        self.detector = ObjectDetector(weights_path=detector_weights)
        self.classifier = WasteClassifier(weights_path=classifier_weights)

    def predict(self, frame: np.ndarray) -> list[tuple[np.ndarray, float, int]]:
        boxes = self.detector.detect(frame)
        if not boxes:
            return []
        crops = self.detector.crop(frame, boxes)
        labels = self.classifier.predict(crops)
        return [
            (
                np.array([b.x1, b.y1, b.x2, b.y2]),
                b.confidence,
                WASTE_CATEGORY_LABELS.index(c.label),
            )
            for b, c in zip(boxes, labels)
        ]


class OneStage:
    def __init__(self, weights: str) -> None:
        detector_config = settings.classification.detector
        self.model = YOLO(weights)
        self.confidence = detector_config.confidence_threshold
        self.image_size = detector_config.image_size
        names = [self.model.names[i] for i in sorted(self.model.names)]
        if tuple(names) != WASTE_CATEGORY_LABELS:
            raise SystemExit(f"Kelas YOLO {names} tidak sama dengan {WASTE_CATEGORY_LABELS}")

    def predict(self, frame: np.ndarray) -> list[tuple[np.ndarray, float, int]]:
        result = self.model.predict(
            source=np.ascontiguousarray(frame[..., ::-1]),
            conf=self.confidence,
            imgsz=self.image_size,
            verbose=False,
        )[0]
        if result.boxes is None or len(result.boxes) == 0:
            return []
        output = [
            (box, float(conf), int(cls))
            for box, conf, cls in zip(
                result.boxes.xyxy.cpu().numpy(),
                result.boxes.conf.cpu().numpy(),
                result.boxes.cls.cpu().numpy(),
            )
            if conf >= self.confidence
        ]
        return sorted(output, key=lambda item: item[1], reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluasi pipeline end-to-end")
    parser.add_argument("--name", required=True, help="Kode eksperimen, mis. P1 atau Y1.")
    parser.add_argument("--mode", choices=["dua-tahap", "satu-tahap"], default="dua-tahap")
    parser.add_argument("--detector-name", default=None, help="Kode detektor, mis. D1.")
    parser.add_argument("--classifier-name", default=None, help="Kode klasifikasi, mis. K1.")
    parser.add_argument("--yolo4-name", default=None, help="Kode YOLO 4 kelas, mis. Y1.")
    parser.add_argument("--detector-weights", default=None)
    parser.add_argument("--classifier-weights", default=None)
    parser.add_argument("--yolo4-weights", default=None)
    parser.add_argument("--split", choices=["val", "test"], default="test")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_CSV)
    parser.add_argument("--clahe", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--multi-object", action="store_true")
    parser.add_argument("--keterangan", default="")
    options = parser.parse_args()

    if options.mode == "dua-tahap":
        detector_weights = options.detector_weights or str(
            detector_weights_path(options.detector_name)
        )
        classifier_weights = options.classifier_weights or str(
            classifier_weights_path(options.classifier_name)
        )
        system = TwoStage(detector_weights, classifier_weights)
        weights_text = f"{detector_weights} + {classifier_weights}"
        description = f"{options.detector_name or 'detektor bawaan'} + {options.classifier_name or 'klasifikasi bawaan'}"
    else:
        yolo4_weights = options.yolo4_weights or str(detector_weights_path(options.yolo4_name))
        system = OneStage(yolo4_weights)
        weights_text = yolo4_weights
        description = f"YOLO 4 kelas {options.yolo4_name or ''}".strip()

    preprocessor = ImagePreprocessor() if options.clahe else None
    rows = [r for r in read_manifest(options.manifest) if r["split"] == options.split]
    if not rows:
        raise SystemExit(f"Tidak ada data split '{options.split}' di manifest")

    per_image = evaluate_images(system, preprocessor, rows, options.name, options.split)
    results = {
        "mode": options.mode,
        "weights": weights_text,
        "clahe": options.clahe,
        "split": options.split,
        "per_citra": per_image,
    }
    if options.multi_object:
        results["multi_objek"] = evaluate_multi_object(system, preprocessor)

    report = write_json_report(
        f"pipeline_evaluation_{options.split}.json", results, options.name
    )
    log_experiment(
        {
            "kode": options.name,
            "tahap": "C-pipeline" if options.mode == "dua-tahap" else "D-yolo-4-kelas",
            "langkah": "evaluasi-pipeline",
            "split": options.split,
            "clahe": options.clahe,
            "keterangan": options.keterangan or description,
            "accuracy": per_image["accuracy"],
            "macro_precision": per_image["macro"]["precision"],
            "macro_recall": per_image["macro"]["recall"],
            "macro_f1": per_image["macro"]["f1"],
            "precision": results.get("multi_objek", {}).get("precision"),
            "recall": results.get("multi_objek", {}).get("recall"),
            "terdeteksi": per_image["detection_rate"],
            "ms_per_citra": per_image["ms_per_image"]["mean"],
            "bobot": weights_text,
            "laporan": report.as_posix(),
        }
    )
    print(
        f"{options.name} ({options.mode}, {options.split}): akurasi {per_image['accuracy']:.4f}, "
        f"F1 makro {per_image['macro']['f1']:.4f}, terdeteksi {per_image['detection_rate']:.4f}"
    )
    print(f"Laporan: {report}")


def load_frame(path: Path, preprocessor: ImagePreprocessor | None) -> np.ndarray:
    bgr = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return preprocessor.process(rgb) if preprocessor else rgb


def timed_predict(system, frame: np.ndarray):
    started_at = time.perf_counter()
    output = system.predict(frame)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    return output, (time.perf_counter() - started_at) * 1000


def evaluate_images(system, preprocessor, rows: list[dict], experiment: str, split: str) -> dict:
    y_true, y_pred, timings, output = [], [], [], []
    for index, row in enumerate(tqdm(rows, desc=f"{experiment} {split}")):
        started_at = time.perf_counter()
        frame = load_frame(PROJECT_ROOT / row["path"], preprocessor)
        clahe_ms = (time.perf_counter() - started_at) * 1000
        predictions, predict_ms = timed_predict(system, frame)
        if index >= 5:
            timings.append(clahe_ms + predict_ms)

        truth = WASTE_CATEGORY_LABELS.index(row["kelas"])
        pred = predictions[0][2] if predictions else MISSED
        y_true.append(truth)
        y_pred.append(pred)
        output.append(
            {
                "path": row["path"],
                "kelas": row["kelas"],
                "subkelas": row["subkelas"],
                "jenis_barang": row["jenis_barang"],
                "prediksi": WASTE_CATEGORY_LABELS[pred] if pred != MISSED else MISSED_LABEL,
                "benar": truth == pred,
                "jumlah_kotak": len(predictions),
                "keyakinan_kotak": round(predictions[0][1], 4) if predictions else "",
            }
        )

    labels = list(range(len(WASTE_CATEGORY_LABELS)))
    macro = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    per_class = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    columns = [*WASTE_CATEGORY_LABELS, MISSED_LABEL]
    matrix = np.zeros((len(labels), len(columns)), dtype=int)
    for truth, pred in zip(y_true, y_pred):
        matrix[truth, pred if pred != MISSED else len(labels)] += 1

    write_csv_report(f"pipeline_predictions_{split}.csv", output, list(output[0]), experiment)
    write_csv_report(
        f"pipeline_confusion_matrix_{split}.csv",
        [
            {"aktual": label, **dict(zip(columns, map(int, matrix[i])))}
            for i, label in enumerate(WASTE_CATEGORY_LABELS)
        ],
        ["aktual", *columns],
        experiment,
    )
    write_per_subclass(output, split, experiment)

    return {
        "images": len(rows),
        "accuracy": float(np.mean(np.array(y_true) == np.array(y_pred))),
        "detection_rate": float(np.mean(np.array(y_pred) != MISSED)),
        "macro": {"precision": float(macro[0]), "recall": float(macro[1]), "f1": float(macro[2])},
        "per_class": {
            label: {
                "precision": float(per_class[0][i]),
                "recall": float(per_class[1][i]),
                "f1": float(per_class[2][i]),
            }
            for i, label in enumerate(WASTE_CATEGORY_LABELS)
        },
        "confusion_matrix": {"columns": columns, "rows_true_cols_pred": matrix.tolist()},
        "ms_per_image": {
            "mean": float(np.mean(timings)) if timings else None,
            "median": float(np.median(timings)) if timings else None,
            "p95": float(np.percentile(timings, 95)) if timings else None,
        },
    }


def write_per_subclass(output: list[dict], split: str, experiment: str) -> None:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in output:
        groups[(row["kelas"], row["subkelas"])].append(row)
    rows = []
    for (kelas, subkelas), items in sorted(groups.items()):
        wrong = Counter(r["prediksi"] for r in items if not r["benar"])
        rows.append(
            {
                "kelas": kelas,
                "subkelas": subkelas,
                "jumlah": len(items),
                "akurasi": round(sum(r["benar"] for r in items) / len(items), 4),
                "tidak_terdeteksi": sum(r["prediksi"] == MISSED_LABEL for r in items),
                "salah_terbanyak_ke": wrong.most_common(1)[0][0] if wrong else "",
            }
        )
    write_csv_report(
        f"pipeline_per_subkelas_{split}.csv",
        rows,
        ["kelas", "subkelas", "jumlah", "akurasi", "tidak_terdeteksi", "salah_terbanyak_ke"],
        experiment,
    )


def evaluate_multi_object(system, preprocessor) -> dict:
    images_dir = MULTI_OBJECT_TEST_DIR / "images"
    labels_dir = MULTI_OBJECT_TEST_DIR / "labels_4kelas"
    if not labels_dir.exists():
        raise SystemExit(
            f"{labels_dir} belum ada. Isi label YOLO 4 kelas (0={WASTE_CATEGORY_LABELS[0]}, "
            f"1={WASTE_CATEGORY_LABELS[1]}, 2={WASTE_CATEGORY_LABELS[2]}, 3={WASTE_CATEGORY_LABELS[3]})."
        )
    true_positive = false_positive = false_negative = localized = 0
    timings: list[float] = []
    image_paths = sorted(p for p in images_dir.glob("*") if p.suffix.lower() in IMAGE_EXTENSIONS)
    for image_path in tqdm(image_paths, desc="Multi-objek"):
        frame = load_frame(image_path, preprocessor)
        height, width = frame.shape[:2]
        truths = read_labels(labels_dir / f"{image_path.stem}.txt", width, height)
        predictions, predict_ms = timed_predict(system, frame)
        timings.append(predict_ms)

        used: set[int] = set()
        for box, _, cls in predictions:
            best_iou, best_index = 0.0, -1
            for index, (truth_box, _) in enumerate(truths):
                if index in used:
                    continue
                overlap = compute_iou(box, truth_box)
                if overlap > best_iou:
                    best_iou, best_index = overlap, index
            if best_iou >= IOU_MATCH_THRESHOLD:
                used.add(best_index)
                localized += 1
                if truths[best_index][1] == cls:
                    true_positive += 1
                else:
                    false_positive += 1
                    false_negative += 1
            else:
                false_positive += 1
        false_negative += len(truths) - len(used)

    precision = true_positive / max(true_positive + false_positive, 1)
    recall = true_positive / max(true_positive + false_negative, 1)
    return {
        "iou_match_threshold": IOU_MATCH_THRESHOLD,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / max(precision + recall, 1e-12),
        "kelas_benar_dari_terlokalisasi": true_positive / max(localized, 1),
        "ms_per_image_mean": float(np.mean(timings)) if timings else None,
    }


def read_labels(path: Path, width: int, height: int) -> list[tuple[np.ndarray, int]]:
    if not path.exists():
        return []
    output = []
    for line in path.read_text(encoding="utf-8").splitlines():
        values = line.split()
        if len(values) != 5:
            continue
        cls = int(values[0])
        cx, cy, w, h = (float(v) for v in values[1:])
        output.append(
            (
                np.array(
                    [(cx - w / 2) * width, (cy - h / 2) * height, (cx + w / 2) * width, (cy + h / 2) * height]
                ),
                cls,
            )
        )
    return output


if __name__ == "__main__":
    main()
