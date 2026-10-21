import argparse
import time
from collections import Counter, defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cv2
import numpy as np
import torch
from tqdm import tqdm
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

from core.config.settings import settings
from core.constants.paths import PROJECT_ROOT
from core.constants.waste import WASTE_CATEGORY_LABELS
from core.utils.device_helper import resolve_torch_device
from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from modules.classification.services.waste_classifier.service import WasteClassifier
from training.common import (
    MANIFEST_CSV,
    classifier_weights_path,
    log_experiment,
    manifest_clahe_baked,
    read_manifest,
    report_dir,
    write_csv_report,
    write_json_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluasi MobileNetV4-Conv-S")
    parser.add_argument("--split", choices=["val", "test"], default="test")
    parser.add_argument(
        "--name", default=None, help="Kode eksperimen (mis. K1); bobot dan laporan per kode."
    )
    parser.add_argument("--weights", default=None, help="Bawaan: bobot milik --name.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_CSV)
    parser.add_argument(
        "--clahe",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Bawaan: mengikuti pengaturan saat training (tersimpan di bobot).",
    )
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--latency-samples", type=int, default=200)
    options = parser.parse_args()
    weights = options.weights or str(classifier_weights_path(options.name))
    clahe = (
        options.clahe
        if options.clahe is not None
        else bool(torch.load(weights, map_location="cpu", weights_only=False).get("clahe", True))
    )

    rows = [row for row in read_manifest(options.manifest) if row["split"] == options.split]
    if not rows:
        raise SystemExit(f"Tidak ada data split '{options.split}' di manifest")

    apply_clahe = clahe and not manifest_clahe_baked(options.manifest)
    preprocessor = ImagePreprocessor() if apply_clahe else None
    classifier = WasteClassifier(weights_path=weights)

    images = [load_rgb(row["path"]) for row in tqdm(rows, desc="Baca citra")]
    enhanced = (
        [preprocessor.process(image) for image in tqdm(images, desc="CLAHE")]
        if apply_clahe
        else images
    )

    classifier.predict(enhanced[: min(8, len(enhanced))])

    predictions = []
    batch_seconds = 0.0
    for start in tqdm(range(0, len(enhanced), options.batch), desc="Prediksi (batch)"):
        batch = enhanced[start : start + options.batch]
        synchronize()
        started_at = time.perf_counter()
        predictions.extend(classifier.predict(batch))
        synchronize()
        batch_seconds += time.perf_counter() - started_at

    latency = measure_single_image_latency(
        preprocessor, classifier, images[: options.latency_samples]
    )

    y_true = [WASTE_CATEGORY_LABELS.index(row["kelas"]) for row in rows]
    y_pred = [WASTE_CATEGORY_LABELS.index(p.label) for p in predictions]
    labels = list(range(len(WASTE_CATEGORY_LABELS)))

    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    macro = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    weighted = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="weighted", zero_division=0
    )

    per_class = {
        label: {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }
        for i, label in enumerate(WASTE_CATEGORY_LABELS)
    }

    split = options.split
    experiment = options.name
    write_predictions(rows, predictions, split, experiment)
    write_confusion_matrix(matrix, split, experiment)
    write_per_subclass(rows, y_true, y_pred, split, experiment)

    accuracy = float(accuracy_score(y_true, y_pred))
    batched_ms = batch_seconds * 1000 / len(rows)
    report = write_json_report(
        f"classifier_evaluation_{split}.json",
        {
            "split": split,
            "weights": weights,
            "clahe": clahe,
            "manifest": options.manifest.as_posix(),
            "images": len(rows),
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "macro": {"precision": macro[0], "recall": macro[1], "f1": macro[2]},
            "weighted": {
                "precision": weighted[0],
                "recall": weighted[1],
                "f1": weighted[2],
            },
            "per_class": per_class,
            "confusion_matrix": {
                "labels": list(WASTE_CATEGORY_LABELS),
                "rows_true_cols_pred": matrix.tolist(),
            },
            "inference": {
                "device": resolve_torch_device(settings.classification.device),
                "batch_size": options.batch,
                "batched_ms_per_image": batched_ms,
                "single_image_ms": latency,
            },
        },
        experiment,
    )
    log_experiment(
        {
            "kode": experiment or "bawaan",
            "tahap": "B-klasifikasi",
            "langkah": "evaluasi",
            "split": split,
            "clahe": clahe,
            "keterangan": f"manifest={options.manifest.parent.name}/{options.manifest.name}",
            "accuracy": accuracy,
            "macro_precision": float(macro[0]),
            "macro_recall": float(macro[1]),
            "macro_f1": float(macro[2]),
            "ms_per_citra": latency["preprocess"]["mean"] + latency["classify"]["mean"],
            "bobot": weights,
            "laporan": report.as_posix(),
        }
    )
    print(f"Akurasi {split}: {accuracy:.4f}  F1 makro: {macro[2]:.4f}")
    print(f"Laporan: {report}")


def load_rgb(relative_path: str) -> np.ndarray:
    bgr = cv2.imdecode(
        np.fromfile(PROJECT_ROOT / relative_path, dtype=np.uint8), cv2.IMREAD_COLOR
    )
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def synchronize() -> None:
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def measure_single_image_latency(
    preprocessor: ImagePreprocessor | None,
    classifier: WasteClassifier,
    images: list[np.ndarray],
) -> dict:
    preprocess_ms, classify_ms = [], []
    for image in tqdm(images, desc="Latensi per citra"):
        started_at = time.perf_counter()
        enhanced = preprocessor.process(image) if preprocessor else image
        preprocessed_at = time.perf_counter()
        classifier.predict([enhanced])
        synchronize()
        finished_at = time.perf_counter()
        preprocess_ms.append((preprocessed_at - started_at) * 1000)
        classify_ms.append((finished_at - preprocessed_at) * 1000)

    def summarize(values: list[float]) -> dict:
        array = np.array(values) if values else np.zeros(1)
        return {
            "mean": float(array.mean()),
            "median": float(np.median(array)),
            "p95": float(np.percentile(array, 95)),
        }

    return {
        "samples": len(images),
        "preprocess": summarize(preprocess_ms),
        "classify": summarize(classify_ms),
    }


def write_predictions(
    rows: list[dict], predictions, split: str, experiment: str | None = None
) -> None:
    output = [
        {
            "path": row["path"],
            "kelas": row["kelas"],
            "subkelas": row["subkelas"],
            "jenis_barang": row["jenis_barang"],
            "prediksi": prediction.label,
            "benar": row["kelas"] == prediction.label,
            **{
                f"p_{label}": round(float(p), 5)
                for label, p in zip(WASTE_CATEGORY_LABELS, prediction.probabilities)
            },
        }
        for row, prediction in zip(rows, predictions)
    ]
    write_csv_report(
        f"classifier_predictions_{split}.csv", output, list(output[0]), experiment
    )


def write_confusion_matrix(
    matrix: np.ndarray, split: str, experiment: str | None = None
) -> None:
    write_csv_report(
        f"classifier_confusion_matrix_{split}.csv",
        [
            {"aktual": label, **dict(zip(WASTE_CATEGORY_LABELS, map(int, matrix[i])))}
            for i, label in enumerate(WASTE_CATEGORY_LABELS)
        ],
        ["aktual", *WASTE_CATEGORY_LABELS],
        experiment,
    )

    figure, axis = plt.subplots(figsize=(6, 5))
    image = axis.imshow(matrix, cmap="Blues")
    axis.set_xticks(range(len(WASTE_CATEGORY_LABELS)), WASTE_CATEGORY_LABELS)
    axis.set_yticks(range(len(WASTE_CATEGORY_LABELS)), WASTE_CATEGORY_LABELS)
    axis.set_xlabel("Prediksi")
    axis.set_ylabel("Aktual")
    threshold = matrix.max() / 2 if matrix.size else 0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            axis.text(
                j,
                i,
                int(matrix[i, j]),
                ha="center",
                va="center",
                color="white" if matrix[i, j] > threshold else "black",
            )
    figure.colorbar(image, ax=axis)
    figure.tight_layout()
    figure.savefig(
        report_dir(experiment) / f"classifier_confusion_matrix_{split}.png", dpi=150
    )
    plt.close(figure)


def write_per_subclass(
    rows: list[dict], y_true, y_pred, split: str, experiment: str | None = None
) -> None:
    groups: dict[tuple[str, str, str], list[tuple[int, int]]] = defaultdict(list)
    for row, true, pred in zip(rows, y_true, y_pred):
        groups[(row["kelas"], row["subkelas"], "")].append((true, pred))
        groups[(row["kelas"], row["subkelas"], row["jenis_barang"])].append((true, pred))

    output = []
    for (kelas, subkelas, jenis_barang), pairs in sorted(groups.items()):
        wrong = Counter(WASTE_CATEGORY_LABELS[p] for t, p in pairs if t != p)
        output.append(
            {
                "kelas": kelas,
                "subkelas": subkelas,
                "jenis_barang": jenis_barang or "(semua)",
                "jumlah": len(pairs),
                "akurasi": round(sum(t == p for t, p in pairs) / len(pairs), 4),
                "salah_terbanyak_ke": wrong.most_common(1)[0][0] if wrong else "",
            }
        )
    write_csv_report(
        f"classifier_per_subkelas_{split}.csv",
        output,
        ["kelas", "subkelas", "jenis_barang", "jumlah", "akurasi", "salah_terbanyak_ke"],
        experiment,
    )


if __name__ == "__main__":
    main()
