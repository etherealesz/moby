import argparse
import shutil

from core.constants.paths import MODELS_DIR
from training.common import DETECTION_DIR, DETECTOR_WEIGHTS, write_json_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tuning YOLO26 satu kelas sampah")
    parser.add_argument("--data", default=str(DETECTION_DIR / "data.yaml"))
    parser.add_argument("--model", default="yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--patience", type=int, default=30)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--device", default="0")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--name", default="yolo26_sampah")
    options = parser.parse_args()

    from ultralytics import YOLO

    model = YOLO(options.model)
    project_dir = MODELS_DIR / "detector_runs"
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
        single_cls=True,
        project=str(project_dir),
        name=options.name,
        exist_ok=True,
    )

    run_dir = project_dir / options.name
    best = run_dir / "weights" / "best.pt"
    DETECTOR_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, DETECTOR_WEIGHTS)

    metrics = YOLO(str(DETECTOR_WEIGHTS)).val(
        data=options.data,
        split="val",
        imgsz=options.imgsz,
        batch=options.batch,
        device=options.device,
        project=str(project_dir),
        name=f"{options.name}_val",
        exist_ok=True,
    )
    report = write_json_report(
        "detector_training.json",
        {
            "base_model": options.model,
            "epochs": options.epochs,
            "imgsz": options.imgsz,
            "batch": options.batch,
            "run_dir": run_dir.as_posix(),
            "weights": DETECTOR_WEIGHTS.as_posix(),
            "val": {
                "precision": float(metrics.box.mp),
                "recall": float(metrics.box.mr),
                "map50": float(metrics.box.map50),
                "map50_95": float(metrics.box.map),
            },
        },
    )
    print(f"Bobot terbaik: {DETECTOR_WEIGHTS}")
    print(f"Laporan: {report}")


if __name__ == "__main__":
    main()
