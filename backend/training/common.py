import csv
import json
import random
import re
import torch
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import numpy as np
from core.constants.paths import DATA_DIR, MODELS_DIR, REPORTS_DIR
from core.constants.waste import WASTE_CATEGORY_LABELS

RAW_DIR = DATA_DIR / "raw"
RAW_MAPPING_CSV = DATA_DIR / "raw_mapping.csv"
MANIFEST_CSV = DATA_DIR / "manifest.csv"
CLASSIFICATION_DIR = DATA_DIR / "classification"
DETECTION_DIR = DATA_DIR / "detection"
DETECTION_RAW_DIR = DATA_DIR / "raw_detection"
MULTI_OBJECT_TEST_DIR = DATA_DIR / "multi_object_test"

CLASSIFIER_WEIGHTS = MODELS_DIR / "classifier" / "best.pt"
DETECTOR_WEIGHTS = MODELS_DIR / "detector" / "best.pt"
DETECTOR_RUNS_DIR = MODELS_DIR / "detector_runs"

EXPERIMENT_LOG_CSV = REPORTS_DIR / "eksperimen_ringkasan.csv"
EXPERIMENT_COLUMNS = [
    "waktu",
    "kode",
    "tahap",
    "langkah",
    "split",
    "clahe",
    "keterangan",
    "accuracy",
    "macro_precision",
    "macro_recall",
    "macro_f1",
    "precision",
    "recall",
    "map50",
    "map50_95",
    "terdeteksi",
    "ms_per_citra",
    "bobot",
    "laporan",
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLITS = ("train", "val", "test")
SPLIT_RATIOS = (0.70, 0.15, 0.15)

MANIFEST_COLUMNS = [
    "path",
    "kelas",
    "subkelas",
    "jenis_barang",
    "sumber",
    "lisensi",
    "split",
    "md5",
    "asal",
]


# Target citra per subkelas. Desain kuota tetap per 2000 (DESIGN_SUBCLASS_TOTAL);
# kuota tiap jenis barang diskalakan proporsional ke target ini. Kembalikan ke 2000
# bila waktu pengumpulan data mencukupi (atau pakai build_dataset --target 2000).
SUBCLASS_TARGET = 2000
DESIGN_SUBCLASS_TOTAL = 2000


@dataclass(frozen=True)
class ItemType:
    kelas: str
    subkelas: str
    jenis_barang: str
    kuota: int  # kuota desain (subkelas berjumlah DESIGN_SUBCLASS_TOTAL)


def _items(kelas: str, subkelas: str, *items: tuple[str, int]) -> list[ItemType]:
    return [ItemType(kelas, subkelas, name, quota) for name, quota in items]


# Tabel 2.1 setelah penyesuaian perancangan (lihat docs/penyesuaian-taksonomi.md).
TAXONOMY: list[ItemType] = [
    *_items("B3", "Baterai", ("baterai AA/AAA", 1000), ("baterai ponsel/lithium", 1000)),
    *_items(
        "B3", "Elektronik Kecil", ("kabel", 700), ("charger", 700), ("earphone", 600)
    ),
    *_items("B3", "Lampu", ("bohlam", 700), ("LED", 700), ("neon", 600)),
    *_items("B3", "Kemasan Bertekanan", ("kaleng aerosol", 1000), ("korek gas", 1000)),
    *_items(
        "Anorganik",
        "Plastik",
        ("botol PET", 700),
        ("plastik kresek polos", 700),
        ("gelas plastik", 600),
    ),
    *_items(
        "Anorganik", "Kertas dan Karton", ("kardus", 1000), ("kertas HVS/koran", 1000)
    ),
    *_items("Anorganik", "Kaca", ("botol kaca", 1620), ("pecahan kaca", 380)),
    *_items("Anorganik", "Logam", ("kaleng minuman", 1000), ("kaleng makanan", 1000)),
    *_items(
        "Anorganik",
        "Tekstil",
        ("pakaian bekas", 1000),
        ("kain perca", 500),
        ("kaus kaki", 500),
    ),
    *_items(
        "Organik", "Sisa Makanan", ("nasi", 1000), ("tulang ayam", 223), ("roti basi", 777)
    ),
    *_items(
        "Organik",
        "Kulit Buah",
        ("kulit pisang", 700),
        ("kulit jeruk", 700),
        ("kulit semangka", 600),
    ),
    *_items(
        "Organik",
        "Sisa Bahan Dapur",
        ("cangkang telur", 840),
        ("kulit bawang", 500),
        ("kulit wortel", 315),
        ("kulit kentang", 345),
    ),
    *_items(
        "Organik",
        "Daun dan Ranting",
        ("daun kering", 932),
        ("ranting", 600),
        ("potongan rumput", 468),
    ),
    *_items(
        "Residu",
        "Produk Sanitasi Sekali Pakai",
        ("masker medis", 1000),
        ("popok", 1000),
    ),
    *_items(
        "Residu",
        "Kemasan Saset",
        ("bungkus mi instan", 139),
        ("saset kopi bubuk", 930),
        ("saset sampo/deterjen", 931),
    ),
    *_items(
        "Residu",
        "Styrofoam",
        ("wadah makanan styrofoam", 1464),
        ("styrofoam pelindung kemasan", 36),
        ("gelas styrofoam", 500),
    ),
    *_items("Residu", "Puntung Rokok", ("puntung rokok", 2000)),
]

TAXONOMY_BY_ITEM: dict[str, ItemType] = {item.jenis_barang: item for item in TAXONOMY}
SUBCLASSES: list[tuple[str, str]] = list(
    dict.fromkeys((item.kelas, item.subkelas) for item in TAXONOMY)
)

assert {item.kelas for item in TAXONOMY} == set(WASTE_CATEGORY_LABELS)
assert len(SUBCLASSES) == 17
for _kelas, _subkelas in SUBCLASSES:
    assert (
        sum(i.kuota for i in TAXONOMY if i.subkelas == _subkelas) == DESIGN_SUBCLASS_TOTAL
    ), _subkelas


def scaled_quotas(target: int = SUBCLASS_TARGET) -> dict[str, int]:
    """Kuota per jenis barang untuk target per subkelas, proporsional terhadap desain.

    Pembulatan memakai sisa terbesar sehingga tiap subkelas berjumlah tepat `target`.
    """
    quotas: dict[str, int] = {}
    for _, subkelas in SUBCLASSES:
        items = [i for i in TAXONOMY if i.subkelas == subkelas]
        exact = [i.kuota * target / DESIGN_SUBCLASS_TOTAL for i in items]
        floors = [int(value) for value in exact]
        order = sorted(
            range(len(items)), key=lambda k: (exact[k] - floors[k], -k), reverse=True
        )
        for k in order[: target - sum(floors)]:
            floors[k] += 1
        quotas.update({item.jenis_barang: q for item, q in zip(items, floors)})
    return quotas


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def seed_everything(seed: int) -> None:

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def read_manifest(path: Path = MANIFEST_CSV) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} belum ada. Jalankan training.build_dataset dulu."
        )
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def manifest_clahe_baked(manifest: Path) -> bool:
    """True bila citra manifest sudah melalui CLAHE (dataset crop dari build_crop_datasets)."""
    info_path = Path(manifest).parent / "dataset_info.json"
    if not info_path.exists():
        return False
    return bool(json.loads(info_path.read_text(encoding="utf-8")).get("clahe_baked"))


def report_dir(experiment: str | None = None) -> Path:
    """Folder laporan: reports/ (bawaan) atau reports/eksperimen/<kode>/."""
    path = REPORTS_DIR / "eksperimen" / experiment if experiment else REPORTS_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def _report_path(name: str, experiment: str | None, directory: Path | None) -> Path:
    if directory is None:
        return report_dir(experiment) / name
    directory.mkdir(parents=True, exist_ok=True)
    return directory / name


def classifier_weights_path(experiment: str | None = None) -> Path:
    if not experiment:
        return CLASSIFIER_WEIGHTS
    return MODELS_DIR / "classifier" / experiment / "best.pt"


def detector_weights_path(experiment: str | None = None) -> Path:
    if not experiment:
        return DETECTOR_WEIGHTS
    return DETECTOR_RUNS_DIR / experiment / "weights" / "best.pt"


def log_experiment(row: dict) -> Path:
    """Tambahkan satu baris hasil ke reports/eksperimen_ringkasan.csv (tidak menimpa)."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    unknown = set(row) - set(EXPERIMENT_COLUMNS)
    if unknown:
        raise ValueError(f"Kolom eksperimen tidak dikenal: {sorted(unknown)}")

    def fmt(value):
        if isinstance(value, float):
            return round(value, 5)
        if isinstance(value, bool):
            return "ya" if value else "tidak"
        return "" if value is None else value

    is_new = not EXPERIMENT_LOG_CSV.exists()
    with open(EXPERIMENT_LOG_CSV, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=EXPERIMENT_COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerow(
            {
                column: fmt(row.get(column))
                for column in EXPERIMENT_COLUMNS
                if column != "waktu"
            }
            | {"waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        )
    return EXPERIMENT_LOG_CSV


def write_json_report(
    name: str, payload: dict, experiment: str | None = None, directory: Path | None = None
) -> Path:
    path = _report_path(name, experiment, directory)
    path.write_text(
        json.dumps(
            {"generated_at": datetime.now().isoformat(), **payload},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def write_csv_report(
    name: str,
    rows: list[dict],
    fieldnames: list[str],
    experiment: str | None = None,
    directory: Path | None = None,
) -> Path:
    path = _report_path(name, experiment, directory)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path
