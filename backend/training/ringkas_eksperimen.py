import csv
from datetime import datetime
from core.constants.paths import REPORTS_DIR
from training.common import EXPERIMENT_LOG_CSV

STAGES = [
    ("A-deteksi", "Tahap A: Deteksi YOLO26 (1 kelas)", "map50_95", ("latih", "val")),
    ("B-klasifikasi", "Tahap B: Klasifikasi MobileNetV4 (4 kelas)", "accuracy", ("evaluasi", "val")),
    ("C-pipeline", "Tahap C: Pipeline dua tahap (YOLO26 + MobileNetV4)", "accuracy", ("evaluasi-pipeline", "val")),
    ("D-yolo-4-kelas", "Tahap D: Pembanding satu tahap (YOLO26 4 kelas)", "accuracy", ("evaluasi-pipeline", "val")),
]
COLUMNS = {
    "A-deteksi": ["precision", "recall", "map50", "map50_95", "ms_per_citra"],
    "B-klasifikasi": ["accuracy", "macro_precision", "macro_recall", "macro_f1", "ms_per_citra"],
    "C-pipeline": ["accuracy", "macro_f1", "terdeteksi", "precision", "recall", "ms_per_citra"],
    "D-yolo-4-kelas": ["accuracy", "macro_f1", "terdeteksi", "map50", "map50_95", "ms_per_citra"],
}

"""
Ringkasan semua eksperimen dari reports/eksperimen_ringkasan.csv.

Skenario terbaik tiap tahap dipilih berdasarkan data validasi; nilai data uji ditampilkan
sebagai hasil akhir (data uji tidak dipakai untuk memilih).
"""


def main() -> None:
    if not EXPERIMENT_LOG_CSV.exists():
        raise SystemExit(f"{EXPERIMENT_LOG_CSV} belum ada. Jalankan training/evaluasi dulu.")
    with open(EXPERIMENT_LOG_CSV, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    latest: dict[tuple, dict] = {}
    for row in rows:
        latest[(row["tahap"], row["kode"], row["langkah"], row["split"])] = row

    lines = [
        "# Ringkasan Eksperimen",
        "",
        f"Dibuat otomatis {datetime.now():%Y-%m-%d %H:%M} dari `{EXPERIMENT_LOG_CSV.name}` "
        f"({len(rows)} baris). Terbaik dipilih dari data **validasi**; data **uji** = hasil akhir.",
    ]
    for stage, title, metric, (select_step, select_split) in STAGES:
        stage_rows = [r for (s, *_), r in latest.items() if s == stage]
        if not stage_rows:
            continue
        codes = sorted({r["kode"] for r in stage_rows})
        lines += ["", f"## {title}", ""]
        header = ["kode", "clahe", "keterangan", f"{metric} (val)", *[f"{c} (uji)" for c in COLUMNS[stage]]]
        lines += ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]

        best_code, best_value = None, -1.0
        for code in codes:
            val_row = latest.get((stage, code, select_step, select_split)) or latest.get(
                (stage, code, "latih", "val")
            )
            test_row = latest.get((stage, code, "evaluasi-pipeline", "test")) or latest.get(
                (stage, code, "evaluasi", "test")
            )
            val_value = to_float(val_row.get(metric)) if val_row else None
            if val_value is not None and val_value > best_value:
                best_code, best_value = code, val_value
            reference = test_row or val_row or {}
            lines.append(
                "| "
                + " | ".join(
                    [
                        code,
                        reference.get("clahe", ""),
                        reference.get("keterangan", ""),
                        fmt(val_value),
                        *[fmt(to_float(test_row.get(c))) if test_row else "-" for c in COLUMNS[stage]],
                    ]
                )
                + " |"
            )
        if best_code:
            lines += ["", f"**Terbaik (validasi): {best_code}** ({metric} = {best_value:.4f})"]

    output = REPORTS_DIR / "eksperimen_ringkasan.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nTersimpan: {output}")


def to_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(value: float | None) -> str:
    return "-" if value is None else f"{value:.4f}"


if __name__ == "__main__":
    main()
