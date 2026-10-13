import argparse
import hashlib
import random
import shutil
from collections import defaultdict
from pathlib import Path
import cv2
import numpy as np
from core.constants.waste import DETECTION_CLASS_NAME
from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from training.common import (
    DETECTION_DIR,
    DETECTION_RAW_DIR,
    IMAGE_EXTENSIONS,
    SPLIT_RATIOS,
    SPLITS,
    write_json_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Menyusun dataset deteksi YOLO satu kelas sampah")
    parser.add_argument("--raw-dir", type=Path, default=DETECTION_RAW_DIR)
    parser.add_argument("--no-clahe", action="store_true")
    parser.add_argument("--keep-unlabeled", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    options = parser.parse_args()

    preprocessor = None if options.no_clahe else ImagePreprocessor()
    samples, stats = collect_samples(options.raw_dir, options.keep_unlabeled)

    rng = random.Random(options.seed)
    samples.sort(key=lambda sample: sample["md5"])
    rng.shuffle(samples)
    n_train = round(len(samples) * SPLIT_RATIOS[0])
    n_val = round(len(samples) * SPLIT_RATIOS[1])
    split_of = (
        ["train"] * n_train
        + ["val"] * n_val
        + ["test"] * (len(samples) - n_train - n_val)
    )

    if DETECTION_DIR.exists():
        shutil.rmtree(DETECTION_DIR)
    for split in SPLITS:
        (DETECTION_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (DETECTION_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)

    split_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"images": 0, "boxes": 0}
    )
    for sample, split in zip(samples, split_of):
        image_target = DETECTION_DIR / "images" / split / f"{sample['md5']}.jpg"
        label_target = DETECTION_DIR / "labels" / split / f"{sample['md5']}.txt"
        write_image(sample["image"], image_target, preprocessor)
        label_target.write_text("\n".join(sample["boxes"]) + "\n", encoding="utf-8")
        split_stats[split]["images"] += 1
        split_stats[split]["boxes"] += len(sample["boxes"])

    yaml_path = DETECTION_DIR / "data.yaml"
    yaml_path.write_text(
        f"path: {DETECTION_DIR.as_posix()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        f"names:\n  0: {DETECTION_CLASS_NAME}\n",
        encoding="utf-8",
    )

    report = write_json_report(
        "detection_dataset.json",
        {
            "clahe": preprocessor is not None,
            "per_sumber": stats,
            "per_split": split_stats,
        },
    )
    print(f"Dataset deteksi: {yaml_path}")
    print(f"Ringkasan: {dict(split_stats)}")
    print(f"Laporan: {report}")


def collect_samples(raw_dir: Path, keep_unlabeled: bool) -> tuple[list[dict], dict]:
    if not raw_dir.exists():
        raise FileNotFoundError(f"{raw_dir} belum ada")

    stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "citra": 0,
            "tanpa_label": 0,
            "label_tidak_valid": 0,
            "duplikat_md5": 0,
            "dipakai": 0,
            "kotak": 0,
        }
    )
    samples: list[dict] = []
    seen_md5: set[str] = set()

    for source_dir in sorted(p for p in raw_dir.iterdir() if p.is_dir()):
        source = source_dir.name
        images = sorted(
            p
            for p in source_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )
        for image_path in images:
            stats[source]["citra"] += 1
            label_path = find_label(image_path)
            if label_path is None and not keep_unlabeled:
                stats[source]["tanpa_label"] += 1
                continue

            boxes = read_single_class_boxes(label_path) if label_path else []
            if boxes is None:
                stats[source]["label_tidak_valid"] += 1
                continue

            md5 = hashlib.md5(image_path.read_bytes()).hexdigest()
            if md5 in seen_md5:
                stats[source]["duplikat_md5"] += 1
                continue
            seen_md5.add(md5)

            samples.append({"image": image_path, "md5": md5, "boxes": boxes})
            stats[source]["dipakai"] += 1
            stats[source]["kotak"] += len(boxes)

    return samples, dict(stats)


def find_label(image_path: Path) -> Path | None:
    parts = list(image_path.parts)
    for index in range(len(parts) - 2, -1, -1):
        if parts[index] == "images":
            parts[index] = "labels"
            label = Path(*parts).with_suffix(".txt")
            return label if label.exists() else None
    label = image_path.with_suffix(".txt")
    return label if label.exists() else None


def read_single_class_boxes(label_path: Path) -> list[str] | None:
    boxes: list[str] = []
    for line in label_path.read_text(encoding="utf-8").splitlines():
        values = line.split()
        if not values:
            continue
        if len(values) != 5:
            if len(values) >= 7 and len(values) % 2 == 1:
                coords = np.array(values[1:], dtype=np.float64).reshape(-1, 2)
                x1, y1 = coords.min(axis=0)
                x2, y2 = coords.max(axis=0)
                values = [
                    "0",
                    str((x1 + x2) / 2),
                    str((y1 + y2) / 2),
                    str(x2 - x1),
                    str(y2 - y1),
                ]
            else:
                return None
        cx, cy, w, h = (float(v) for v in values[1:])
        if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 < w <= 1 and 0 < h <= 1):
            return None
        boxes.append(f"0 {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return boxes


def write_image(
    source: Path, target: Path, preprocessor: ImagePreprocessor | None
) -> None:
    bgr = cv2.imdecode(np.fromfile(source, dtype=np.uint8), cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f"Citra tidak dapat dibaca: {source}")
    if preprocessor is not None:
        rgb = preprocessor.process(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    ok, buffer = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ok:
        raise ValueError(f"Gagal menyimpan {target}")
    buffer.tofile(target)


if __name__ == "__main__":
    main()
