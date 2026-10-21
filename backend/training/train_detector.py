import argparse
import shutil
from pathlib import Path
from ultralytics import YOLO
from training.build_detection_dataset import read_dataset_info
from training.common import (
    DETECTION_DIR,
    DETECTOR_RUNS_DIR,
    DETECTOR_WEIGHTS,
    log_experiment,
    write_json_report,
)

DEFAULT_RUN_NAME = "yolo26_sampah"


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tuning YOLO26")
    parser.add_argument("--data", default=str(DETECTION_DIR / "data.yaml"))
    parser.add_argument("--model", default="yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--patience", type=int, default=30)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--device", default="0")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--name",
        default=DEFAULT_RUN_NAME,
        help="Kode eksperimen (mis. D1). Selain nama bawaan, bobot tidak menimpa "
        "models/detector/best.pt dan laporan masuk reports/eksperimen/<kode>/.",
    )
    parser.add_argument("--keterangan", default="", help="Catatan singkat eksperimen.")
    options = parser.parse_args()

    info = read_dataset_info(Path(options.data))
    single_class = len(info["names"]) == 1
    experiment = None if options.name == DEFAULT_RUN_NAME else options.name

    model = YOLO(options.model)
    model.train(
        data=options.data,
        epochs=options.epochs,
        imgsz=options.imgsz,
        batch=options.batch,
        patience=options.patience,
        workers=options.workers,
        device=options.device,
        seed=options.seed,
        amp=True,
        single_cls=single_class,
        project=str(DETECTOR_RUNS_DIR),
        name=options.name,
        exist_ok=True,
    )

    run_dir = DETECTOR_RUNS_DIR / options.name
    weights = run_dir / "weights" / "best.pt"
    if experiment is None:
        DETECTOR_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(weights, DETECTOR_WEIGHTS)
        weights = DETECTOR_WEIGHTS

    metrics = YOLO(str(weights)).val(
        data=options.data,
        split="val",
        imgsz=options.imgsz,
        batch=options.batch,
        device=options.device,
        project=str(DETECTOR_RUNS_DIR),
        name=f"{options.name}_val",
        exist_ok=True,
    )
    val = {
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "map50": float(metrics.box.map50),
        "map50_95": float(metrics.box.map),
    }
    report = write_json_report(
        "detector_training.json",
        {
            "base_model": options.model,
            "data": options.data,
            "classes": info["names"],
            "clahe": info["clahe"],
            "epochs": options.epochs,
            "imgsz": options.imgsz,
            "batch": options.batch,
            "run_dir": run_dir.as_posix(),
            "weights": weights.as_posix(),
            "val": val,
        },
        experiment,
    )
    log_experiment(
        {
            "kode": experiment or "bawaan",
            "tahap": "A-deteksi" if single_class else "D-yolo-4-kelas",
            "langkah": "latih",
            "split": "val",
            "clahe": info["clahe"],
            "keterangan": options.keterangan or f"{options.model}, {len(info['names'])} kelas",
            **val,
            "bobot": weights.as_posix(),
            "laporan": report.as_posix(),
        }
    )
    print(f"Bobot terbaik: {weights}")
    print(f"Laporan: {report}")


if __name__ == "__main__":
    main()
