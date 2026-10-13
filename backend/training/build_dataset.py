import argparse
import csv
import hashlib
import random
import shutil
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np
from core.constants.paths import PROJECT_ROOT
from training.common import (
    CLASSIFICATION_DIR,
    IMAGE_EXTENSIONS,
    MANIFEST_COLUMNS,
    MANIFEST_CSV,
    RAW_DIR,
    RAW_MAPPING_CSV,
    SPLIT_RATIOS,
    SPLITS,
    TAXONOMY,
    TAXONOMY_BY_ITEM,
    slugify,
    write_csv_report,
    write_json_report,
)


@dataclass
class Candidate:
    order: int
    sumber: str
    lisensi: str
    jenis_barang: str
    path: Path
    md5: str = ""
    phash: int = 0
    readable: bool = True


def main() -> None:
    parser = argparse.ArgumentParser(description="Menyusun dataset klasifikasi 17 subkelas")
    parser.add_argument("--mapping", type=Path, default=RAW_MAPPING_CSV)
    parser.add_argument(
        "--phash-threshold",
        type=int,
        default=6,
        help="Jarak Hamming pHash maksimum untuk dianggap hampir sama (0..64).",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=8)
    options = parser.parse_args()

    candidates = collect_candidates(options.mapping)
    print(f"Kandidat dari raw_mapping: {len(candidates)} file")

    with ThreadPoolExecutor(max_workers=options.workers) as pool:
        list(pool.map(compute_hashes, candidates))

    kept, stats = deduplicate(candidates, options.phash_threshold)
    selected, shortages = select_by_quota(kept, options.seed)
    rows = write_dataset(selected, options.seed)

    for row in rows:
        stats[row["sumber"]]["dipakai"] += 1

    dedup_path = write_json_report(
        "dedup_report.json",
        {
            "phash_threshold": options.phash_threshold,
            "per_sumber": stats,
            "total": {
                key: sum(s[key] for s in stats.values())
                for key in next(iter(stats.values()), {})
            },
        },
    )
    shortage_path = write_csv_report(
        "kuota_kurang.csv",
        shortages,
        ["kelas", "subkelas", "jenis_barang", "kuota", "tersedia", "kurang"],
    )

    split_counts = Counter((row["split"], row["kelas"]) for row in rows)
    print(f"Manifest: {MANIFEST_CSV} ({len(rows)} citra)")
    for split in SPLITS:
        per_class = {k: v for (s, k), v in sorted(split_counts.items()) if s == split}
        print(f"  {split}: {per_class}")
    print(f"Laporan dedup: {dedup_path}")
    print(
        f"Kekurangan kuota: {shortage_path} "
        f"({sum(s['kurang'] for s in shortages)} citra kurang)"
    )


def collect_candidates(mapping_path: Path) -> list[Candidate]:
    if not mapping_path.is_absolute():
        mapping_path = PROJECT_ROOT / mapping_path
    if not mapping_path.exists():
        raise FileNotFoundError(
            f"{mapping_path} belum ada. Buat file dengan kolom: "
            "sumber,pola,jenis_barang,lisensi"
        )

    candidates: list[Candidate] = []
    seen_paths: set[Path] = set()
    with open(mapping_path, newline="", encoding="utf-8-sig") as file:
        for line_number, row in enumerate(csv.DictReader(file), start=2):
            jenis_barang = row["jenis_barang"].strip()
            if jenis_barang not in TAXONOMY_BY_ITEM:
                raise ValueError(
                    f"Baris {line_number}: jenis_barang '{jenis_barang}' tidak ada di "
                    "Tabel 2.1"
                )

            source_dir = RAW_DIR / row["sumber"].strip()
            matches = sorted(
                path
                for path in source_dir.glob(row["pola"].strip())
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
            )
            if not matches:
                print(f"Peringatan baris {line_number}: pola tidak cocok dengan file")

            for path in matches:
                resolved = path.resolve()
                if resolved in seen_paths:
                    continue
                seen_paths.add(resolved)
                candidates.append(
                    Candidate(
                        order=len(candidates),
                        sumber=row["sumber"].strip(),
                        lisensi=row.get("lisensi", "").strip(),
                        jenis_barang=jenis_barang,
                        path=path,
                    )
                )
    return candidates


def compute_hashes(candidate: Candidate) -> None:
    data = candidate.path.read_bytes()
    candidate.md5 = hashlib.md5(data).hexdigest()

    image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if image is None:
        candidate.readable = False
        return
    candidate.phash = perceptual_hash(image)


def perceptual_hash(gray: np.ndarray) -> int:
    resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32)
    low = cv2.dct(resized)[:8, :8].flatten()
    median = np.median(low[1:])
    bits = low > median
    return int(np.packbits(bits).view(">u8")[0])


def deduplicate(
    candidates: list[Candidate],
    threshold: int,
) -> tuple[list[Candidate], dict[str, dict[str, int]]]:
    stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "kandidat": 0,
            "rusak": 0,
            "duplikat_md5": 0,
            "duplikat_phash": 0,
            "lolos_dedup": 0,
            "dipakai": 0,
        }
    )

    unique: list[Candidate] = []
    seen_md5: set[str] = set()
    for candidate in candidates:
        stats[candidate.sumber]["kandidat"] += 1
        if not candidate.readable:
            stats[candidate.sumber]["rusak"] += 1
        elif candidate.md5 in seen_md5:
            stats[candidate.sumber]["duplikat_md5"] += 1
        else:
            seen_md5.add(candidate.md5)
            unique.append(candidate)

    neighbors = near_duplicate_pairs(unique, threshold)
    kept: list[Candidate] = []
    kept_indices: set[int] = set()
    for index, candidate in enumerate(unique):
        if neighbors.get(index, set()) & kept_indices:
            stats[candidate.sumber]["duplikat_phash"] += 1
            continue
        kept_indices.add(index)
        kept.append(candidate)
        stats[candidate.sumber]["lolos_dedup"] += 1

    return kept, dict(stats)


def near_duplicate_pairs(
    candidates: list[Candidate], threshold: int
) -> dict[int, set[int]]:
    if not candidates:
        return {}

    hashes = np.array([c.phash for c in candidates], dtype=np.uint64)
    band_count = threshold + 1
    edges = np.linspace(0, 64, band_count + 1).astype(int)
    neighbors: dict[int, set[int]] = defaultdict(set)

    for start, end in zip(edges[:-1], edges[1:]):
        width = end - start
        mask = np.uint64((1 << width) - 1)
        band = (hashes >> np.uint64(64 - end)) & mask
        order = np.argsort(band, kind="stable")
        sorted_band = band[order]
        boundaries = np.flatnonzero(np.diff(sorted_band)) + 1
        for group in np.split(order, boundaries):
            if len(group) < 2:
                continue
            group_hashes = hashes[group]
            distances = np.bitwise_count(group_hashes[:, None] ^ group_hashes[None, :])
            rows, cols = np.nonzero(np.triu(distances <= threshold, k=1))
            for i, j in zip(group[rows], group[cols]):
                neighbors[int(i)].add(int(j))
                neighbors[int(j)].add(int(i))
    return neighbors


def select_by_quota(
    kept: list[Candidate],
    seed: int,
) -> tuple[dict[str, list[Candidate]], list[dict]]:
    by_item: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in kept:
        by_item[candidate.jenis_barang].append(candidate)

    rng = random.Random(seed)
    selected: dict[str, list[Candidate]] = {}
    shortages: list[dict] = []
    for item in TAXONOMY:
        pool = sorted(by_item.get(item.jenis_barang, []), key=lambda c: c.md5)
        rng.shuffle(pool)
        selected[item.jenis_barang] = pool[: item.kuota]
        if len(pool) < item.kuota:
            shortages.append(
                {
                    "kelas": item.kelas,
                    "subkelas": item.subkelas,
                    "jenis_barang": item.jenis_barang,
                    "kuota": item.kuota,
                    "tersedia": len(pool),
                    "kurang": item.kuota - len(pool),
                }
            )
    return selected, shortages


def split_counts(total: int) -> tuple[int, int, int]:
    n_train = round(total * SPLIT_RATIOS[0])
    n_val = round(total * SPLIT_RATIOS[1])
    return n_train, n_val, total - n_train - n_val


def write_dataset(selected: dict[str, list[Candidate]], seed: int) -> list[dict]:
    if CLASSIFICATION_DIR.exists():
        shutil.rmtree(CLASSIFICATION_DIR)

    rng = random.Random(seed + 1)
    rows: list[dict] = []
    for item in TAXONOMY:
        pool = list(selected[item.jenis_barang])
        rng.shuffle(pool)
        n_train, n_val, _ = split_counts(len(pool))
        assignments = (
            [("train", c) for c in pool[:n_train]]
            + [("val", c) for c in pool[n_train : n_train + n_val]]
            + [("test", c) for c in pool[n_train + n_val :]]
        )

        for split, candidate in assignments:
            target_dir = (
                CLASSIFICATION_DIR
                / split
                / item.kelas
                / item.subkelas
                / slugify(item.jenis_barang)
            )
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / f"{candidate.md5}{candidate.path.suffix.lower()}"
            shutil.copy2(candidate.path, target)
            rows.append(
                {
                    "path": target.relative_to(PROJECT_ROOT).as_posix(),
                    "kelas": item.kelas,
                    "subkelas": item.subkelas,
                    "jenis_barang": item.jenis_barang,
                    "sumber": candidate.sumber,
                    "lisensi": candidate.lisensi,
                    "split": split,
                    "md5": candidate.md5,
                    "asal": candidate.path.relative_to(PROJECT_ROOT).as_posix(),
                }
            )

    MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    main()
