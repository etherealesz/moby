import argparse
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support
from core.constants.paths import REPORTS_DIR
from training.common import log_experiment, report_dir

"""Perbandingan confusion matrix K1 vs K2 dan P2 vs Y1 pada split uji yang sama.

Dibangun dari prediksi per citra hasil evaluate_classifier.py / evaluate_pipeline.py
(tidak ada inferensi ulang). Kelas citra P2/Y1 = kelas kotak paling yakin; citra tanpa
deteksi masuk kolom "Tidak terdeteksi".
"""

CLASSES = ["Anorganik", "B3", "Organik", "Residu"]
MISSED = "Tidak terdeteksi"
OUTPUT_DIR = REPORTS_DIR / "confusion"
CMAP = "Blues"
DIFF_CMAP = "RdBu"
DPI = 300
SCENARIOS = {
    "K1": ("classifier_predictions", "B-klasifikasi", "MobileNetV4 tanpa CLAHE"),
    "K2": ("classifier_predictions", "B-klasifikasi", "MobileNetV4 + CLAHE"),
    "P2": ("pipeline_predictions", "C-pipeline", "D4 + K1 (dua tahap)"),
    "Y1": ("pipeline_predictions", "D-yolo-4-kelas", "YOLO26 4 kelas (satu tahap)"),
}
PAIRS = [("K1", "K2"), ("P2", "Y1")]


def load_predictions(code: str, split: str) -> pd.DataFrame:
    prefix = SCENARIOS[code][0]
    path = report_dir(code) / f"{prefix}_{split}.csv"
    if not path.exists():
        raise SystemExit(f"Prediksi {code} tidak ditemukan: {path}")
    frame = pd.read_csv(path)
    frame["prediksi"] = frame["prediksi"].replace({"tidak terdeteksi": MISSED})
    return frame


def columns_for(frame: pd.DataFrame) -> list[str]:
    return CLASSES + [MISSED] if "jumlah_kotak" in frame.columns else CLASSES


def confusion(frame: pd.DataFrame, rows_key: str, rows: list[str], cols: list[str]) -> pd.DataFrame:
    table = pd.crosstab(frame[rows_key], frame["prediksi"])
    return table.reindex(index=rows, columns=cols, fill_value=0)


def row_percent(matrix: pd.DataFrame) -> pd.DataFrame:
    return matrix.div(matrix.sum(axis=1).replace(0, 1), axis=0) * 100


def metrics(frame: pd.DataFrame) -> dict:
    precision, recall, f1, _ = precision_recall_fscore_support(
        frame["kelas"], frame["prediksi"], labels=CLASSES, average="macro", zero_division=0
    )
    return {
        "accuracy": float((frame["kelas"] == frame["prediksi"]).mean()),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "macro_f1": float(f1),
        "tidak_terdeteksi": int((frame["prediksi"] == MISSED).sum()),
    }


def draw(axis, matrix: pd.DataFrame, title: str, percent: bool, diff: bool = False) -> None:
    values = matrix.to_numpy(dtype=float)
    if diff:
        limit = max(np.abs(values).max(), 1.0)
        image = axis.imshow(values, cmap=DIFF_CMAP, vmin=-limit, vmax=limit, aspect="auto")
    else:
        image = axis.imshow(values, cmap=CMAP, vmin=0, vmax=100 if percent else values.max(), aspect="auto")
    threshold = (np.abs(values).max() or 1) * 0.6
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            v = values[i, j]
            text = f"{v:+.1f}" if diff else (f"{v:.1f}%" if percent else f"{int(v)}")
            axis.text(j, i, text, ha="center", va="center", fontsize=8,
                      color="white" if abs(v) > threshold else "black")
    axis.set_xticks(range(values.shape[1]), matrix.columns, rotation=30, ha="right", fontsize=8)
    axis.set_yticks(range(values.shape[0]), matrix.index, fontsize=8)
    axis.set_xlabel("Prediksi")
    axis.set_ylabel("Label sebenarnya")
    axis.set_title(title, fontsize=10)
    plt.colorbar(image, ax=axis, fraction=0.046, pad=0.04,
                 label="Selisih (poin persen)" if diff else ("Persen per baris" if percent else "Jumlah citra"))


def save_figure(matrices: list[tuple[pd.DataFrame, str, bool, bool]], name: str, height: float = 4.5) -> Path:
    fig, axes = plt.subplots(1, len(matrices), figsize=(6.2 * len(matrices), height), squeeze=False)
    for axis, (matrix, title, percent, diff) in zip(axes[0], matrices):
        draw(axis, matrix, title, percent, diff)
    fig.tight_layout()
    path = OUTPUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path


def save_csv(matrix: pd.DataFrame, name: str, decimals: int | None = None) -> None:
    out = matrix.round(decimals) if decimals is not None else matrix
    out.rename_axis("Label sebenarnya").to_csv(OUTPUT_DIR / f"{name}.csv", encoding="utf-8")


def top_confusions(raw: pd.DataFrame, k: int = 5) -> list[tuple[str, str, int, float]]:
    totals = raw.sum(axis=1)
    pairs = [
        (t, p, int(raw.loc[t, p]), raw.loc[t, p] / totals[t] * 100)
        for t in CLASSES for p in CLASSES if t != p and raw.loc[t, p] > 0
    ]
    return sorted(pairs, key=lambda item: item[2], reverse=True)[:k]


def main() -> None:
    parser = argparse.ArgumentParser(description="Perbandingan confusion matrix K1/K2 dan P2/Y1")
    parser.add_argument("--split", choices=["val", "test"], default="test")
    parser.add_argument("--no-log", action="store_true", help="Jangan tambah baris ke eksperimen_ringkasan.csv")
    options = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    frames = {code: load_predictions(code, options.split) for code in SCENARIOS}
    reference = frames["K1"].set_index("path").index
    for code, frame in frames.items():
        if not frame.set_index("path").index.sort_values().equals(reference.sort_values()):
            raise SystemExit(f"Citra uji {code} tidak sama dengan K1")

    raw, pct, summary = {}, {}, {}
    for code, frame in frames.items():
        cols = columns_for(frame)
        raw[code] = confusion(frame, "kelas", CLASSES, cols)
        pct[code] = row_percent(raw[code])
        summary[code] = metrics(frame)
        label = f"{code}: {SCENARIOS[code][2]}"
        save_csv(raw[code], f"{code}_mentah")
        save_csv(pct[code], f"{code}_persen", 2)
        save_figure([(raw[code], label, False, False)], f"{code}_mentah")
        save_figure([(pct[code], label, True, False)], f"{code}_persen")

    for a, b in PAIRS:
        save_figure(
            [(pct[a], f"{a}: {SCENARIOS[a][2]}", True, False), (pct[b], f"{b}: {SCENARIOS[b][2]}", True, False)],
            f"{a}_vs_{b}_persen",
        )
        diff = pct[a] - pct[b]
        save_csv(diff, f"selisih_{a}_minus_{b}", 2)
        save_figure([(diff, f"Selisih {a} − {b} (poin persen)", True, True)], f"selisih_{a}_minus_{b}")

    subclasses = sorted(frames["K1"]["subkelas"].unique())
    for code in ("K1", "P2"):
        frame = frames[code]
        cols = columns_for(frame)
        order = frame.drop_duplicates("subkelas").set_index("subkelas")["kelas"]
        rows = sorted(subclasses, key=lambda s: (CLASSES.index(order[s]), s))
        sub_raw = confusion(frame, "subkelas", rows, cols)
        sub_raw.index = [f"{s} ({order[s]})" for s in rows]
        sub_pct = row_percent(sub_raw)
        save_csv(sub_raw, f"{code}_subkelas_mentah")
        save_csv(sub_pct, f"{code}_subkelas_persen", 2)
        save_figure([(sub_pct, f"{code}: 17 subkelas × kelas prediksi", True, False)], f"{code}_subkelas_persen", 8)

    write_summary(summary, raw, options.split)
    if not options.no_log:
        for code, values in summary.items():
            log_experiment(
                {
                    "kode": code,
                    "tahap": SCENARIOS[code][1],
                    "langkah": "perbandingan-confusion",
                    "split": options.split,
                    "keterangan": f"confusion matrix dari prediksi tersimpan; {SCENARIOS[code][2]}",
                    "accuracy": values["accuracy"],
                    "macro_precision": values["macro_precision"],
                    "macro_recall": values["macro_recall"],
                    "macro_f1": values["macro_f1"],
                    "terdeteksi": 1 - values["tidak_terdeteksi"] / len(frames[code])
                    if code in ("P2", "Y1") else None,
                    "laporan": (OUTPUT_DIR / "ringkasan.md").as_posix(),
                }
            )
    print(f"Keluaran: {OUTPUT_DIR}")


def write_summary(summary: dict, raw: dict, split: str) -> None:
    lines = [
        f"# Ringkasan confusion matrix (split {split})",
        "",
        "Dibuat oleh `training/compare_confusion.py` dari prediksi per citra di `reports/eksperimen/<kode>/`.",
        "Macro precision/recall/F1 dihitung atas 4 kelas; citra \"Tidak terdeteksi\" dihitung salah.",
        "",
        "| Skenario | Keterangan | Accuracy | Macro precision | Macro recall | Macro F1 | Tidak terdeteksi |",
        "|---|---|---|---|---|---|---|",
    ]
    for code, v in summary.items():
        missed = str(v["tidak_terdeteksi"]) if code in ("P2", "Y1") else "-"
        lines.append(
            f"| {code} | {SCENARIOS[code][2]} | {v['accuracy']*100:.2f}% | {v['macro_precision']*100:.2f}% "
            f"| {v['macro_recall']*100:.2f}% | {v['macro_f1']*100:.2f}% | {missed} |"
        )
    for code in SCENARIOS:
        lines += ["", f"## Lima pasangan kelas paling sering tertukar: {code}", "",
                  "| Label sebenarnya | Prediksi | Jumlah | % dari baris |", "|---|---|---|---|"]
        lines += [f"| {t} | {p} | {n} | {r:.2f}% |" for t, p, n, r in top_confusions(raw[code])]
    (OUTPUT_DIR / "ringkasan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
