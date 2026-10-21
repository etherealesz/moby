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
from tqdm import tqdm
from core.constants.paths import DOCS_REPORTS_DIR, PROJECT_ROOT
from training.common import (
    CLASSIFICATION_DIR,
    IMAGE_EXTENSIONS,
    MANIFEST_COLUMNS,
    MANIFEST_CSV,
    RAW_DIR,
    RAW_MAPPING_CSV,
    SPLIT_RATIOS,
    SPLITS,
    SUBCLASS_TARGET,
    SUBCLASSES,
    TAXONOMY,
    TAXONOMY_BY_ITEM,
    scaled_quotas,
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
    parser.add_argument(
        "--target",
        type=int,
        default=SUBCLASS_TARGET,
        help="Citra per subkelas; kuota jenis barang diskalakan dari desain 2000.",
    )
    parser.add_argument(
        "--isi-augmentasi",
        action="store_true",
        help="Tutup kekurangan subkelas dengan augmentasi offline dari citra train "
        "(hanya split train; val/test tetap citra asli).",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=8)
    options = parser.parse_args()

    candidates = collect_candidates(options.mapping)
    print(f"Kandidat dari raw_mapping: {len(candidates)} file")

    with ThreadPoolExecutor(max_workers=options.workers) as pool:
        list(tqdm(pool.map(compute_hashes, candidates), total=len(candidates), desc="Hash MD5/pHash"))

    kept, stats = deduplicate(candidates, options.phash_threshold)
    selected, shortages = select_by_quota(kept, options.seed, options.target)
    rows = write_dataset(selected, options.seed)
    augmented = (
        augment_to_target(rows, options.target, options.seed) if options.isi_augmentasi else []
    )
    if augmented:
        write_manifest(rows + augmented)
        write_csv_report(
            "augmentasi_offline.csv",
            [{k: r[k] for k in AUGMENT_REPORT_COLUMNS} for r in augmented],
            AUGMENT_REPORT_COLUMNS,
            directory=DOCS_REPORTS_DIR,
        )
        print(f"Augmentasi offline (train saja): {len(augmented)} citra, "
              f"rincian di docs/reports/augmentasi_offline.csv")
        rows = rows + augmented

    for row in rows:
        if row["sumber"] != AUGMENT_SOURCE:
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
        directory=DOCS_REPORTS_DIR,
    )
    shortage_path = write_csv_report(
        "kuota_kurang.csv",
        shortages,
        ["kelas", "subkelas", "jenis_barang", "kuota", "tersedia", "dipakai", "kurang"],
        directory=DOCS_REPORTS_DIR,
    )

    split_counts = Counter((row["split"], row["kelas"]) for row in rows)
    print(f"Manifest: {MANIFEST_CSV} ({len(rows)} citra, target {options.target}/subkelas)")
    for split in SPLITS:
        per_class = {k: v for (s, k), v in sorted(split_counts.items()) if s == split}
        print(f"  {split}: {per_class}")
    print(f"Laporan dedup: {dedup_path}")
    print(
        f"Kekurangan kuota: {shortage_path} "
        f"({sum(s['kurang'] for s in shortages if s['jenis_barang'] == SUBCLASS_ROW)} "
        "citra kurang setelah ditutup jenis lain dalam subkelas)"
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


SUBCLASS_ROW = "(subkelas)"


def select_by_quota(
    kept: list[Candidate],
    seed: int,
    target: int,
) -> tuple[dict[str, list[Candidate]], list[dict]]:
    """Ambil kuota tiap jenis barang; kekurangan suatu jenis ditutup jenis lain yang
    berlebih dalam subkelas yang sama (bergiliran), tidak pernah dengan augmentasi."""
    by_item: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in kept:
        by_item[candidate.jenis_barang].append(candidate)

    quotas = scaled_quotas(target)
    rng = random.Random(seed)
    pools: dict[str, list[Candidate]] = {}
    for item in TAXONOMY:
        pool = sorted(by_item.get(item.jenis_barang, []), key=lambda c: c.md5)
        rng.shuffle(pool)
        pools[item.jenis_barang] = pool

    selected: dict[str, list[Candidate]] = {}
    shortages: list[dict] = []
    for kelas, subkelas in SUBCLASSES:
        items = [i.jenis_barang for i in TAXONOMY if i.subkelas == subkelas]
        taken = {name: min(len(pools[name]), quotas[name]) for name in items}
        deficit = target - sum(taken.values())
        while deficit > 0:
            spare = [name for name in items if taken[name] < len(pools[name])]
            if not spare:
                break
            for name in spare[:deficit]:
                taken[name] += 1
                deficit -= 1

        for name in items:
            selected[name] = pools[name][: taken[name]]
            if len(pools[name]) < quotas[name] or taken[name] != quotas[name]:
                shortages.append(
                    {
                        "kelas": kelas,
                        "subkelas": subkelas,
                        "jenis_barang": name,
                        "kuota": quotas[name],
                        "tersedia": len(pools[name]),
                        "dipakai": taken[name],
                        "kurang": max(quotas[name] - len(pools[name]), 0),
                    }
                )
        used = sum(taken.values())
        if used < target:
            shortages.append(
                {
                    "kelas": kelas,
                    "subkelas": subkelas,
                    "jenis_barang": SUBCLASS_ROW,
                    "kuota": target,
                    "tersedia": sum(len(pools[name]) for name in items),
                    "dipakai": used,
                    "kurang": target - used,
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
    progress = tqdm(total=sum(len(v) for v in selected.values()), desc="Salin ke data/classification")
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
            progress.update()
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

    progress.close()
    write_manifest(rows)
    return rows


def write_manifest(rows: list[dict]) -> None:
    MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=MANIFEST_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


AUGMENT_SOURCE = "augmentasi"
AUGMENT_REPORT_COLUMNS = ["path", "kelas", "subkelas", "jenis_barang", "asal", "operasi"]


def augment_to_target(rows: list[dict], target: int, seed: int) -> list[dict]:
    """Tambah citra augmentasi ke split train hingga tiap subkelas berjumlah `target`.

    Sumber hanya citra train subkelas yang sama (diutamakan jenis barang yang kurang dari
    kuotanya), sehingga tidak ada informasi val/test yang masuk ke train.
    """
    quotas = scaled_quotas(target)
    rng = random.Random(seed + 2)
    output: list[dict] = []
    for _, subkelas in SUBCLASSES:
        members = [r for r in rows if r["subkelas"] == subkelas]
        deficit = target - len(members)
        if deficit <= 0:
            continue
        used = Counter(r["jenis_barang"] for r in members)
        train = [r for r in members if r["split"] == "train"]
        short = [r for r in train if used[r["jenis_barang"]] < quotas[r["jenis_barang"]]]
        sources = sorted(short or train, key=lambda r: r["md5"])
        if not sources:
            continue
        rng.shuffle(sources)
        for k in tqdm(range(deficit), desc=f"Augmentasi {subkelas}"):
            source = sources[k % len(sources)]
            image = cv2.imdecode(
                np.fromfile(PROJECT_ROOT / source["path"], dtype=np.uint8), cv2.IMREAD_COLOR
            )
            augmented, operations = random_augment(image, rng)
            ok, buffer = cv2.imencode(".jpg", augmented, [cv2.IMWRITE_JPEG_QUALITY, 92])
            if not ok:
                raise ValueError(f"Gagal augmentasi {source['path']}")
            target_path = (PROJECT_ROOT / source["path"]).parent / (
                f"aug{k // len(sources) + 1}_{source['md5']}.jpg"
            )
            buffer.tofile(target_path)
            output.append(
                {
                    **source,
                    "path": target_path.relative_to(PROJECT_ROOT).as_posix(),
                    "sumber": AUGMENT_SOURCE,
                    "md5": hashlib.md5(buffer.tobytes()).hexdigest(),
                    "asal": source["path"],
                    "operasi": operations,
                }
            )
    return output


def random_augment(image: np.ndarray, rng: random.Random) -> tuple[np.ndarray, str]:
    """Flip horizontal, rotasi +-25 derajat, crop 80-100%, kecerahan/kontras +-15%."""
    operations = []
    if rng.random() < 0.5:
        image = cv2.flip(image, 1)
        operations.append("flip")
    height, width = image.shape[:2]
    angle = rng.uniform(-25, 25)
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    image = cv2.warpAffine(image, matrix, (width, height), borderMode=cv2.BORDER_REFLECT_101)
    operations.append(f"rotasi{angle:+.0f}")
    scale = rng.uniform(0.8, 1.0)
    crop_h, crop_w = int(height * scale), int(width * scale)
    top, left = rng.randint(0, height - crop_h), rng.randint(0, width - crop_w)
    image = image[top : top + crop_h, left : left + crop_w]
    operations.append(f"crop{scale:.2f}")
    alpha, beta = rng.uniform(0.85, 1.15), rng.uniform(-20, 20)
    image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    operations.append(f"kontras{alpha:.2f}_terang{beta:+.0f}")
    return image, "+".join(operations)


if __name__ == "__main__":
    main()
