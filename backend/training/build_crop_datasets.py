import argparse
import csv
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path
import cv2
import numpy as np
from tqdm import tqdm
from core.constants.paths import DATA_DIR, PROJECT_ROOT
from core.constants.waste import WASTE_CATEGORY_LABELS
from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from modules.classification.services.object_detector.service import ObjectDetector
from training.build_detection_dataset import write_dataset_info
from training.common import (
    MANIFEST_COLUMNS,
    MANIFEST_CSV,
    SPLITS,
    detector_weights_path,
    read_manifest,
    slugify,
    write_json_report,
)

CROPS_DIR = DATA_DIR / "classification_crops"
DETECTION_4_CLASS_DIR = DATA_DIR / "detection_4kelas"


def main() -> None:
    parser = argparse.ArgumentParser(description="Dataset crop (K4) dan YOLO 4 kelas (D)")
    parser.add_argument("--detector-name", default=None, help="Kode detektor, mis. D1.")
    parser.add_argument("--detector-weights", default=None)
    parser.add_argument("--clahe", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--crops-out", type=Path, default=CROPS_DIR)
    parser.add_argument("--detection-out", type=Path, default=DETECTION_4_CLASS_DIR)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_CSV)
    options = parser.parse_args()
    options.crops_out = options.crops_out.resolve()
    options.detection_out = options.detection_out.resolve()

    weights = options.detector_weights or str(detector_weights_path(options.detector_name))
    detector = ObjectDetector(weights_path=weights)
    preprocessor = ImagePreprocessor() if options.clahe else None
    rows = read_manifest(options.manifest)

    for folder in (options.crops_out, options.detection_out):
        if folder.exists():
            shutil.rmtree(folder)
    for split in SPLITS:
        (options.detection_out / "images" / split).mkdir(parents=True, exist_ok=True)
        (options.detection_out / "labels" / split).mkdir(parents=True, exist_ok=True)

    crop_rows: list[dict] = []
    stats: dict[str, Counter] = defaultdict(Counter)
    for row in tqdm(rows, desc="Deteksi + crop"):
        split = row["split"]
        bgr = cv2.imdecode(
            np.fromfile(PROJECT_ROOT / row["path"], dtype=np.uint8), cv2.IMREAD_COLOR
        )
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        frame = preprocessor.process(rgb) if preprocessor else rgb
        boxes = detector.detect(frame)
        height, width = frame.shape[:2]

        if boxes:
            stats[split]["terdeteksi"] += 1
            crop = detector.crop(frame, boxes[:1])[0]
        else:
            stats[split]["tidak_terdeteksi"] += 1
            crop = frame

        crop_target = (
            options.crops_out
            / split
            / row["kelas"]
            / row["subkelas"]
            / slugify(row["jenis_barang"])
            / f"{row['md5']}.jpg"
        )
        save_rgb(crop, crop_target)
        crop_rows.append(
            {**row, "path": crop_target.relative_to(PROJECT_ROOT).as_posix()}
        )

        if boxes:
            class_id = WASTE_CATEGORY_LABELS.index(row["kelas"])
            save_rgb(frame, options.detection_out / "images" / split / f"{row['md5']}.jpg")
            labels = [
                f"{class_id} {(b.x1 + b.x2) / 2 / width:.6f} {(b.y1 + b.y2) / 2 / height:.6f} "
                f"{(b.x2 - b.x1) / width:.6f} {(b.y2 - b.y1) / height:.6f}"
                for b in boxes
            ]
            (options.detection_out / "labels" / split / f"{row['md5']}.txt").write_text(
                "\n".join(labels) + "\n", encoding="utf-8"
            )
            stats[split]["kotak"] += len(boxes)

    manifest_path = options.crops_out / "manifest.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows({k: r.get(k, "") for k in MANIFEST_COLUMNS} for r in crop_rows)
    write_dataset_info(options.crops_out, clahe=options.clahe, names=list(WASTE_CATEGORY_LABELS))
    mark_clahe_baked(options.crops_out)

    (options.detection_out / "data.yaml").write_text(
        f"path: {options.detection_out.resolve().as_posix()}\n"
        "train: images/train\nval: images/val\ntest: images/test\nnames:\n"
        + "".join(f"  {i}: {name}\n" for i, name in enumerate(WASTE_CATEGORY_LABELS)),
        encoding="utf-8",
    )
    write_dataset_info(
        options.detection_out, clahe=options.clahe, names=list(WASTE_CATEGORY_LABELS)
    )

    report = write_json_report(
        "crop_datasets.json",
        {
            "detector_weights": weights,
            "clahe": options.clahe,
            "confidence_threshold": detector.confidence_threshold,
            "crops_manifest": manifest_path.as_posix(),
            "detection_4kelas": options.detection_out.as_posix(),
            "per_split": {split: dict(counter) for split, counter in stats.items()},
            "catatan": "Citra tanpa deteksi: crop = citra utuh (K4), "
            "dan tidak dimasukkan ke dataset YOLO 4 kelas.",
        },
    )
    print(f"Manifest crop: {manifest_path}")
    print(f"Dataset YOLO 4 kelas: {options.detection_out / 'data.yaml'}")
    print(f"Laporan: {report}")


def mark_clahe_baked(folder: Path) -> None:
    """Crop sudah melalui CLAHE; train/evaluate_classifier tidak menerapkannya lagi."""
    info_path = folder / "dataset_info.json"
    info = json.loads(info_path.read_text(encoding="utf-8"))
    info["clahe_baked"] = info["clahe"]
    info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")


def save_rgb(rgb: np.ndarray, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    ok, buffer = cv2.imencode(
        ".jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 95]
    )
    if not ok:
        raise ValueError(f"Gagal menyimpan {target}")
    buffer.tofile(target)


if __name__ == "__main__":
    main()
