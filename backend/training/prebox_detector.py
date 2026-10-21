import argparse
from collections import Counter, defaultdict
from pathlib import Path
import cv2
import numpy as np
from tqdm import tqdm
from core.constants.paths import DATA_DIR, PROJECT_ROOT
from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from modules.classification.services.object_detector.service import ObjectDetector
from training.common import (
    MANIFEST_CSV,
    SPLITS,
    detector_weights_path,
    read_manifest,
    write_json_report,
)

"""Kotak awal dari detektor hasil latih (mis. D4) untuk review_boxes.

Format keluaran sama dengan Dataset_Final/_autobox: OUT/<Subkelas>/labels/<nama asal>.txt.
Foto tanpa deteksi tetap mendapat file kosong agar proses bisa dilanjutkan.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Kotak awal dari detektor untuk review_boxes")
    parser.add_argument("--detector-name", default="D4")
    parser.add_argument("--detector-weights", default=None)
    parser.add_argument("--split", nargs="+", choices=SPLITS, default=["train"])
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--clahe", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_CSV)
    parser.add_argument("--out", type=Path, default=None)
    options = parser.parse_args()

    weights = options.detector_weights or str(detector_weights_path(options.detector_name))
    out = options.out or DATA_DIR / "raw_detection_review" / f"_prebox_{options.detector_name}"
    detector = ObjectDetector(weights_path=weights, confidence_threshold=options.conf)
    preprocessor = ImagePreprocessor() if options.clahe else None

    rows = [
        r
        for r in read_manifest(options.manifest)
        if r["split"] in options.split and r["sumber"] != "augmentasi"
    ]
    stats: dict[str, Counter] = defaultdict(Counter)
    for row in tqdm(rows, desc=f"Pra-kotak {options.detector_name}"):
        asal = Path(row["asal"])
        label = out / asal.parent.name / "labels" / f"{asal.stem}.txt"
        if label.exists():
            stats[row["split"]]["sudah_ada"] += 1
            continue
        bgr = cv2.imdecode(np.fromfile(PROJECT_ROOT / asal, dtype=np.uint8), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        frame = preprocessor.process(rgb) if preprocessor else rgb
        boxes = detector.detect(frame)
        height, width = frame.shape[:2]
        label.parent.mkdir(parents=True, exist_ok=True)
        label.write_text(
            "".join(
                f"0 {(b.x1 + b.x2) / 2 / width:.6f} {(b.y1 + b.y2) / 2 / height:.6f} "
                f"{(b.x2 - b.x1) / width:.6f} {(b.y2 - b.y1) / height:.6f}\n"
                for b in boxes
            ),
            encoding="utf-8",
        )
        stats[row["split"]]["ada_kotak" if boxes else "tanpa_kotak"] += 1

    report = write_json_report(
        f"prebox_{options.detector_name}.json",
        {
            "detector_weights": weights,
            "clahe": options.clahe,
            "confidence_threshold": options.conf,
            "out": out.as_posix(),
            "per_split": {split: dict(counter) for split, counter in stats.items()},
        },
    )
    print(f"Kotak awal: {out}")
    print(f"Laporan: {report}")


if __name__ == "__main__":
    main()
