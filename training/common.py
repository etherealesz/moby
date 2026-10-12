import csv
import json
import random
import re
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


@dataclass(frozen=True)
class ItemType:
    kelas: str
    subkelas: str
    jenis_barang: str
    kuota: int


def _items(kelas: str, subkelas: str, *items: tuple[str, int]) -> list[ItemType]:
    return [ItemType(kelas, subkelas, name, quota) for name, quota in items]


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
    *_items("Anorganik", "Kaca", ("botol kaca", 1200), ("pecahan kaca", 800)),
    *_items("Anorganik", "Logam", ("kaleng minuman", 1000), ("kaleng makanan", 1000)),
    *_items(
        "Anorganik",
        "Tekstil",
        ("pakaian bekas", 1000),
        ("kain perca", 500),
        ("kaus kaki", 500),
    ),
    *_items("Organik", "Sisa Makanan", ("nasi", 1000), ("tulang ayam", 1000)),
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
        ("cangkang telur", 500),
        ("kulit bawang", 500),
        ("kulit wortel", 500),
        ("kulit kentang", 500),
    ),
    *_items(
        "Organik",
        "Daun dan Ranting",
        ("daun kering", 800),
        ("ranting", 600),
        ("potongan rumput", 600),
    ),
    *_items(
        "Residu",
        "Produk Sanitasi Sekali Pakai",
        ("masker medis", 700),
        ("popok", 700),
        ("pembalut", 600),
    ),
    *_items(
        "Residu",
        "Kemasan Saset",
        ("bungkus mi instan", 700),
        ("saset kopi bubuk", 700),
        ("saset sampo/deterjen", 600),
    ),
    *_items(
        "Residu",
        "Styrofoam",
        ("wadah makanan styrofoam", 1000),
        ("styrofoam pelindung kemasan", 1000),
    ),
    *_items("Residu", "Puntung Rokok", ("puntung rokok", 2000)),
]

TAXONOMY_BY_ITEM: dict[str, ItemType] = {item.jenis_barang: item for item in TAXONOMY}

assert {item.kelas for item in TAXONOMY} == set(WASTE_CATEGORY_LABELS)
assert len({(item.kelas, item.subkelas) for item in TAXONOMY}) == 17


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def seed_everything(seed: int) -> None:
    import torch

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


def write_json_report(name: str, payload: dict) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / name
    path.write_text(
        json.dumps(
            {"generated_at": datetime.now().isoformat(), **payload},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def write_csv_report(name: str, rows: list[dict], fieldnames: list[str]) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / name
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path
