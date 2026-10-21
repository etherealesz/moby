import argparse
import csv
import random
import shutil
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
from core.constants.paths import DATA_DIR, PROJECT_ROOT, REPORTS_DIR
from training.common import MANIFEST_CSV, RAW_DIR, SPLITS, read_manifest, write_json_report

"""Review kotak deteksi pada foto dataset klasifikasi (bahan eksperimen D4, D5, ...).

Foto diambil acak per subkelas dari data/manifest.csv (tanpa citra augmentasi) pada split
yang dipilih. Split mengikuti manifest, jadi foto val/test klasifikasi tetap val/test.
Kotak awal dicari berurutan di setiap --autobox-dir (mis. _prebox_D4 lalu _autobox
YOLO-World); bila tidak ada, kotak digambar manual. Tombol d tidak menghapus foto asli,
foto hanya tidak dimasukkan ke data deteksi.

Tombol:
  Enter/Spasi : terima kotak yang tampil
  drag mouse  : tambah kotak (kapan saja)
  z           : hapus kotak terakhir
  r           : hapus semua kotak (lalu drag untuk menggambar ulang)
  d           : buang foto ini
  b           : kembali ke foto sebelumnya (keputusan terakhir dibatalkan)
  s           : lewati ke subkelas berikutnya
  q / Esc     : simpan dan keluar (bisa dilanjutkan kapan saja)

Keluaran tanpa --name (D4):
  data/raw_detection_review/dataset_final/images|labels
  reports/review_kotak.csv, reports/review_kotak_ringkasan.json
Keluaran dengan --name N:
  data/raw_detection_review/N/images|labels/<split>/  (format YOLO, kelas 0 "sampah")
  reports/review_kotak_N.csv, reports/review_kotak_N_ringkasan.json
"""

LEGACY_NAME = "dataset_final"
DEFAULT_AUTOBOX_DIR = (RAW_DIR / "dataset_final").resolve().parent / "_autobox"
LOG_COLUMNS = [
    "waktu",
    "split",
    "subkelas",
    "jenis_barang",
    "asal",
    "md5",
    "keputusan",
    "sumber_kotak",
    "kotak_awal",
    "kotak_akhir",
]
WINDOW = "Review kotak"
MAX_SIDE = 900
Box = tuple[float, float, float, float]  # cx, cy, w, h ternormalisasi


@dataclass(frozen=True)
class Store:
    folder: Path
    log_csv: Path
    summary_name: str
    per_split: bool

    @classmethod
    def of(cls, name: str | None) -> "Store":
        if name is None or name == LEGACY_NAME:
            return cls(
                DATA_DIR / "raw_detection_review" / LEGACY_NAME,
                REPORTS_DIR / "review_kotak.csv",
                "review_kotak_ringkasan.json",
                per_split=False,
            )
        return cls(
            DATA_DIR / "raw_detection_review" / name,
            REPORTS_DIR / f"review_kotak_{name}.csv",
            f"review_kotak_{name}_ringkasan.json",
            per_split=True,
        )

    def images(self, split: str) -> Path:
        return self.folder / "images" / split if self.per_split else self.folder / "images"

    def labels(self, split: str) -> Path:
        return self.folder / "labels" / split if self.per_split else self.folder / "labels"


def main() -> None:
    parser = argparse.ArgumentParser(description="Review kotak deteksi foto dataset klasifikasi")
    parser.add_argument("--name", default=None, help="Nama hasil review, mis. D5 (bawaan: D4)")
    parser.add_argument("--split", nargs="+", choices=SPLITS, default=["train"])
    parser.add_argument("--per-subkelas", type=int, default=150, help="0 = semua foto")
    parser.add_argument(
        "--subkelas", nargs="*", help="Mis. Plastik Lampu (bawaan: semua)"
    )
    parser.add_argument(
        "--autobox-dir",
        type=Path,
        nargs="+",
        default=[DEFAULT_AUTOBOX_DIR],
        help="Sumber kotak awal, dipakai berurutan (yang pertama punya kotak menang).",
    )
    parser.add_argument(
        "--impor-dari",
        default=None,
        help="Salin keputusan review lain yang belum ada, mis. dataset_final (hasil D4).",
    )
    parser.add_argument("--seed", type=int, default=42)
    options = parser.parse_args()

    store = Store.of(options.name)
    for split in options.split:
        store.images(split).mkdir(parents=True, exist_ok=True)
        store.labels(split).mkdir(parents=True, exist_ok=True)

    groups: dict[str, list[dict]] = defaultdict(list)
    by_md5: dict[str, dict] = {}
    for row in read_manifest(MANIFEST_CSV):
        if row["split"] in options.split and row["sumber"] != "augmentasi":
            groups[row["subkelas"]].append(row)
            by_md5[row["md5"]] = row
    if options.impor_dari:
        import_decisions(Store.of(options.impor_dari), store, by_md5)

    decided, accepted = read_log(store)
    wanted = options.subkelas or sorted(groups)
    history = [by_md5[md5] for md5 in read_log_order(store) if md5 in by_md5]
    target = options.per_subkelas or max(len(rows) for rows in groups.values())

    cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)
    try:
        for subkelas in wanted:
            rows = sorted(
                groups.get(subkelas.replace("_", " "), []), key=lambda r: r["md5"]
            )
            random.Random(options.seed).shuffle(rows)
            rows.sort(key=lambda r: not initial_boxes(r, options.autobox_dir)[0])
            pending = deque(r for r in rows if r["md5"] not in decided)
            while pending:
                row = pending.popleft()
                if row["md5"] in decided:
                    continue
                if accepted[row["subkelas"]] >= target:
                    break
                action = review_one(row, options, store, accepted, target)
                if action == "keluar":
                    return
                if action == "lewati":
                    break
                if action == "kembali":
                    pending.appendleft(row)
                    if history:
                        previous = history.pop()
                        undo(previous, store, decided, accepted)
                        pending.appendleft(previous)
                    continue
                decided.add(row["md5"])
                history.append(row)
    finally:
        cv2.destroyAllWindows()
        summarize(store)


def review_one(row: dict, options, store: Store, accepted: Counter, target: int) -> str:
    source = PROJECT_ROOT / row["asal"]
    image = cv2.imdecode(np.fromfile(source, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return "lanjut"
    view = fit(image)
    initial, origin = initial_boxes(row, options.autobox_dir)
    state = {"boxes": list(initial), "start": None, "end": None, "edited": False}
    cv2.setMouseCallback(WINDOW, on_mouse, (state, view.shape[1], view.shape[0]))
    message = "" if initial else "Tidak ada kotak otomatis: drag mouse untuk menggambar"

    while True:
        show(view, state, row, accepted, target, origin, message)
        key = cv2.waitKey(20)
        if key == -1:
            continue
        key &= 0xFF
        message = ""
        if key in (13, 32):
            if not state["boxes"]:
                message = (
                    "Belum ada kotak: drag mouse untuk menggambar, atau d untuk buang"
                )
                continue
            if not state["edited"]:
                decision = "diterima"
            else:
                decision = "diubah" if initial else "digambar"
            save(row, source, store, state["boxes"])
            log(store, row, decision, origin, initial, state["boxes"])
            accepted[row["subkelas"]] += 1
            return "lanjut"
        if key == ord("r"):
            state["boxes"].clear()
            state["edited"] = True
            message = "Kotak dihapus: drag mouse untuk menggambar kotak baru"
        elif key == ord("z") and state["boxes"]:
            state["boxes"].pop()
            state["edited"] = True
        elif key == ord("d"):
            log(store, row, "dibuang", origin, initial, [])
            return "lanjut"
        elif key == ord("b"):
            return "kembali"
        elif key == ord("s"):
            return "lewati"
        elif key in (ord("q"), 27):
            return "keluar"


def on_mouse(event, x, y, _flags, param) -> None:
    """Drag kiri = tambah kotak. Koordinat disimpan ternormalisasi terhadap tampilan."""
    state, width, height = param
    x, y = min(max(x, 0), width - 1), min(max(y, 0), height - 1)
    if event == cv2.EVENT_LBUTTONDOWN:
        state["start"], state["end"] = (x, y), (x, y)
    elif event == cv2.EVENT_MOUSEMOVE and state["start"]:
        state["end"] = (x, y)
    elif event == cv2.EVENT_LBUTTONUP and state["start"]:
        (x1, y1), (x2, y2) = state["start"], (x, y)
        state["start"] = state["end"] = None
        if abs(x2 - x1) >= 5 and abs(y2 - y1) >= 5:
            left, top = min(x1, x2), min(y1, y2)
            w, h = abs(x2 - x1), abs(y2 - y1)
            state["boxes"].append(
                ((left + w / 2) / width, (top + h / 2) / height, w / width, h / height)
            )
            state["edited"] = True


def initial_boxes(row: dict, autobox_dirs: list[Path]) -> tuple[list[Box], str]:
    for autobox_dir in autobox_dirs:
        boxes = autobox_boxes(row, autobox_dir)
        if boxes:
            return boxes, origin_name(autobox_dir)
    return [], "manual"


def origin_name(autobox_dir: Path) -> str:
    if autobox_dir.name.startswith("_prebox_"):
        return autobox_dir.name.removeprefix("_prebox_")
    if autobox_dir.name == "_autobox":
        return "yolo-world"
    return autobox_dir.name


def autobox_boxes(row: dict, autobox_dir: Path) -> list[Box]:
    subfolder = Path(row["asal"]).parent.name
    label = autobox_dir / subfolder / "labels" / f"{Path(row['asal']).stem}.txt"
    if not label.exists():
        return []
    boxes = []
    for line in label.read_text(encoding="utf-8").split("\n"):
        values = line.split()
        if len(values) == 5:
            boxes.append(tuple(float(v) for v in values[1:]))
    return boxes


def fit(image: np.ndarray) -> np.ndarray:
    scale = min(1.0, MAX_SIDE / max(image.shape[:2]))
    if scale < 1.0:
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return image


def show(view, state, row, accepted, target, origin, message) -> None:
    canvas = view.copy()
    height, width = canvas.shape[:2]
    for cx, cy, w, h in state["boxes"]:
        x1, y1 = int((cx - w / 2) * width), int((cy - h / 2) * height)
        x2, y2 = int((cx + w / 2) * width), int((cy + h / 2) * height)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 0), 2)
    if state["start"] and state["end"]:
        cv2.rectangle(canvas, state["start"], state["end"], (0, 200, 255), 2)
    lines = [
        f"[{row['split']}] {row['subkelas']} / {row['jenis_barang']}  "
        f"diterima {accepted[row['subkelas']]}/{target}",
        f"kotak: {len(state['boxes'])} ({origin})  drag=tambah kotak  z=hapus kotak terakhir",
        "Enter=terima  r=hapus semua  d=buang  b=kembali  s=lewati  q=keluar",
    ]
    if message:
        lines.append(message)
    for index, text in enumerate(lines):
        y = 22 + index * 22
        color = (0, 220, 255) if text == message else (255, 255, 255)
        cv2.putText(canvas, text, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 4)
        cv2.putText(canvas, text, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)
    cv2.imshow(WINDOW, canvas)


def save(row: dict, source: Path, store: Store, boxes: list[Box]) -> None:
    split = row["split"]
    shutil.copy2(source, store.images(split) / f"{row['md5']}{source.suffix.lower()}")
    (store.labels(split) / f"{row['md5']}.txt").write_text(
        "".join(f"0 {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n" for cx, cy, w, h in boxes),
        encoding="utf-8",
    )


def log(
    store: Store,
    row: dict,
    decision: str,
    origin: str,
    initial: list[Box],
    final: list[Box],
) -> None:
    write_log_entry(
        store,
        {
            "waktu": datetime.now().isoformat(timespec="seconds"),
            "split": row["split"],
            "subkelas": row["subkelas"],
            "jenis_barang": row["jenis_barang"],
            "asal": row["asal"],
            "md5": row["md5"],
            "keputusan": decision,
            "sumber_kotak": origin,
            "kotak_awal": len(initial),
            "kotak_akhir": len(final),
        },
    )


def write_log_entry(store: Store, entry: dict) -> None:
    new = not store.log_csv.exists()
    columns = LOG_COLUMNS if new else log_columns(store)
    store.log_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(store.log_csv, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        if new:
            writer.writeheader()
        writer.writerow({k: entry.get(k, "") for k in columns})


def log_columns(store: Store) -> list[str]:
    """Log D4 lama belum punya kolom split; header yang ada tetap dipakai."""
    with open(store.log_csv, newline="", encoding="utf-8") as file:
        return next(csv.reader(file))


def read_log_entries(store: Store) -> list[dict]:
    if not store.log_csv.exists():
        return []
    with open(store.log_csv, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def import_decisions(source: Store, target: Store, by_md5: dict[str, dict]) -> None:
    """Salin keputusan (dan file foto + label) dari review lain yang belum ada di target."""
    known = {entry["md5"] for entry in read_log_entries(target)}
    imported = 0
    for entry in read_log_entries(source):
        row = by_md5.get(entry["md5"])
        if row is None or entry["md5"] in known:
            continue
        split = row["split"]
        if entry["keputusan"] != "dibuang":
            for image in source.images(split).glob(f"{entry['md5']}.*"):
                shutil.copy2(image, target.images(split) / image.name)
            shutil.copy2(
                source.labels(split) / f"{entry['md5']}.txt",
                target.labels(split) / f"{entry['md5']}.txt",
            )
        write_log_entry(target, {**entry, "split": split})
        known.add(entry["md5"])
        imported += 1
    print(f"Diimpor dari {source.folder.name}: {imported} keputusan")


def read_log_order(store: Store) -> list[str]:
    return [entry["md5"] for entry in read_log_entries(store)]


def undo(row: dict, store: Store, decided: set[str], accepted: Counter) -> None:
    """Batalkan keputusan terakhir untuk foto ini: hapus baris log dan file hasilnya."""
    entries = read_log_entries(store)
    index = max(i for i, entry in enumerate(entries) if entry["md5"] == row["md5"])
    removed = entries.pop(index)
    columns = log_columns(store)
    with open(store.log_csv, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows({k: entry.get(k, "") for k in columns} for entry in entries)
    if removed["keputusan"] != "dibuang":
        accepted[row["subkelas"]] -= 1
        for path in store.images(row["split"]).glob(f"{row['md5']}.*"):
            path.unlink()
        (store.labels(row["split"]) / f"{row['md5']}.txt").unlink(missing_ok=True)
    decided.discard(row["md5"])


def read_log(store: Store) -> tuple[set[str], Counter]:
    decided: set[str] = set()
    accepted: Counter = Counter()
    for entry in read_log_entries(store):
        decided.add(entry["md5"])
        if entry["keputusan"] != "dibuang":
            accepted[entry["subkelas"]] += 1
    return decided, accepted


def summarize(store: Store) -> None:
    entries = read_log_entries(store)
    if not entries:
        return
    per_subclass: dict[str, Counter] = defaultdict(Counter)
    per_split: dict[str, Counter] = defaultdict(Counter)
    per_origin: dict[str, Counter] = defaultdict(Counter)
    for entry in entries:
        per_subclass[entry["subkelas"]][entry["keputusan"]] += 1
        per_split[entry.get("split") or "train"][entry["keputusan"]] += 1
        per_origin[entry["sumber_kotak"]][entry["keputusan"]] += 1
    total = Counter(entry["keputusan"] for entry in entries)
    report = write_json_report(
        store.summary_name,
        {
            "folder": store.folder.as_posix(),
            "total": dict(total),
            "per_split": {k: dict(v) for k, v in sorted(per_split.items())},
            "per_sumber_kotak": {k: dict(v) for k, v in sorted(per_origin.items())},
            "per_subkelas": {k: dict(v) for k, v in sorted(per_subclass.items())},
            "catatan": "diterima = kotak awal benar tanpa diubah; diubah = kotak awal "
            "dikoreksi manual; digambar = tanpa kotak awal, digambar manual; dibuang = foto "
            "tidak dipakai untuk deteksi (foto asli tidak dihapus).",
        },
    )
    print(f"Ringkasan review: {dict(total)}")
    print(f"Laporan: {report}")


if __name__ == "__main__":
    main()
