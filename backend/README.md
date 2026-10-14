# MOBY Backend

Backend MOBY: klasifikasi citra sampah (CLAHE, YOLO26, MobileNetV4-Conv-S,
penghalusan temporal) dan navigasi rute A* ke fasilitas pengelolaan sampah di
DKI Jakarta, Kota Tangerang, Kota Depok, dan Kota Bekasi.

Stack: FastAPI, PostgreSQL (SQLAlchemy async + Alembic), PyTorch (CUDA 12.8),
Ultralytics, timm, OpenCV, OSMnx.

## Struktur

```
src/
├── app/                 # FastAPI: factory, middleware, exception handler, route setup
├── container/           # dependency injection (injector)
├── core/                # config, konstanta, enum, util (Haversine, device)
├── infrastructures/     # DatabaseManager, session, model dasar
├── commands/            # command CLI: seed_database, extract_road_graph, evaluate_navigation
└── modules/
    ├── classification/  # ImagePreprocessor, ObjectDetector, WasteClassifier, TemporalSmoother
    ├── navigation/      # RoadGraphManager, NavigationService (A*), Road_Node, Road_Edge
    ├── facilities/      # Facility, Facility_Category
    ├── waste_categories/# WasteCategory, WasteSubcategory
    ├── info/            # konten halaman Tentang dan Bantuan
    └── etc/             # health check
training/                # build dataset, pelatihan, evaluasi model
scripts/                 # runner command + migrasi Alembic
files/config/            # local.yaml, production.yaml
docs/                    # keputusan.md, schema.sql, contoh format CSV
data/  models/  reports/ # dataset, bobot, hasil evaluasi (dibuat saat dijalankan)
```

Setiap modul mengikuti pola template:

```
modules/<modul>/
├── container.py                 # registrasi DI
├── models/                      # model SQLAlchemy (tabel)
├── repositories/<nama>/         # protocol.py (interface) + repository.py (implementasi)
├── services/<nama>/service.py   # logika domain (kelas dari proposal)
├── use_cases/<nama>/use_case.py # orkestrasi satu kebutuhan bisnis
├── routers/<nama>/router.py     # endpoint (Controller)
├── schemas/  mappers/  exceptions/
```

Alur data: Router (schema `S...`) -> Use case (DTO `D...`) -> Service/Repository ->
PostgreSQL. Tidak ada cache. Graf jalan dibaca dari `road_node`/`road_edge` di
setiap permintaan rute (lihat `docs/keputusan.md`).

## Endpoint

| Metode | Path | Fungsi |
|---|---|---|
| GET | `/moby/health` | health check |
| POST | `/moby/api/classify` | satu frame (multipart `file`, JPEG/PNG) -> objek: box, label, confidence |
| WS | `/moby/ws/classify` | kirim frame JPEG (biner), terima JSON; teks `reset` mengosongkan TemporalSmoother |
| POST | `/moby/api/route` | `{latitude, longitude, category, network_type}` -> fasilitas, rute, jarak |
| GET | `/moby/api/categories` | Waste_Category beserta Waste_Subcategory |
| GET | `/moby/api/facilities` | daftar Facility, filter `category`, `city`, `query`, `page`, `page_size` |
| GET | `/moby/api/info/about` | konten halaman Tentang |
| GET | `/moby/api/info/help` | konten halaman Bantuan |

Dokumentasi interaktif: `http://localhost:8000/docs`.

## Setup

Prasyarat: Python 3.11, [uv](https://docs.astral.sh/uv/), PostgreSQL, GPU NVIDIA
(opsional untuk inferensi, sangat disarankan untuk pelatihan).

```bash
uv sync --all-groups --no-group deployment   # pasang dependensi (torch CUDA 12.8)
uv run pre-commit install                    # opsional
```

Atur koneksi database di `files/config/local.yaml`.

### Database

```bash
# 1. Buat / perbarui skema (6 tabel Lampiran 9).
#    Migrasi a1c3e5f7b9d2 menyalin osm_nodes/osm_edges lama ke road_node/road_edge
#    lalu menghapus tabel lama.
uv run alembic upgrade head

# 2. Isi kategori, subkategori, fasilitas, dan Facility_Category.
#    Fasilitas dibaca dari data/geo/facilities.csv (format: docs/contoh/facilities.csv).
uv run python -m scripts.commands run seed_database

# 3. (Opsional) unduh ulang graf jalan OSM ke road_node/road_edge.
uv run python -m scripts.commands run extract_road_graph --network-type all
uv run python -m scripts.commands run extract_road_graph --network-type walk --place "Kota Depok, Jawa Barat, Indonesia"
```

### Menjalankan server

```bash
uv run fastapi dev main.py
```

Endpoint klasifikasi membutuhkan `models/detector/best.pt` dan
`models/classifier/best.pt` (hasil pelatihan di bawah). Tanpa bobot, endpoint
mengembalikan 503 `DETECTOR_MODEL_NOT_AVAILABLE` / `CLASSIFIER_MODEL_NOT_AVAILABLE`;
endpoint lain tetap berjalan.

## Pelatihan model

Semua perintah dijalankan dari folder `backend/`. Setiap angka hasil ditulis ke
`reports/` oleh script, tidak diketik manual.

### Klasifikasi (MobileNetV4-Conv-S, 4 kelas)

1. Letakkan dataset mentah di `data/raw/<nama_sumber>/` (tidak diubah).
2. Buat `data/raw_mapping.csv` yang memetakan pola file ke jenis barang Tabel 2.1
   (contoh: `docs/contoh/raw_mapping.csv`).
3. Susun dataset (dedup MD5 + pHash, kuota, split 70:15:15 per jenis barang):

   ```bash
   uv run python -m training.build_dataset
   ```

   Hasil: `data/classification/`, `data/manifest.csv`, `reports/dedup_report.json`,
   `reports/kuota_kurang.csv` (jumlah foto mandiri yang masih harus diambil).
4. Latih (fase beku backbone, lalu fine-tuning; AdamW, cross-entropy, AMP):

   ```bash
   uv run python -m training.train_classifier
   ```

   Hasil: `models/classifier/best.pt` (akurasi validasi terbaik),
   `reports/classifier_training*.{json,csv,png}`.
5. Evaluasi **sekali** pada data uji:

   ```bash
   uv run python -m training.evaluate_classifier
   ```

   Hasil: confusion matrix (CSV + PNG), accuracy, precision, recall, F1 per kelas,
   metrik per subkelas dan jenis barang, waktu inferensi.

### Deteksi (YOLO26, satu kelas `sampah`)

1. Letakkan dataset berformat YOLO di `data/raw_detection/<nama_sumber>/`
   (misal `train/images`, `train/labels`).
2. Gabungkan menjadi satu kelas dan split ulang 70:15:15 (CLAHE diterapkan):

   ```bash
   uv run python -m training.build_detection_dataset
   ```

3. Latih:

   ```bash
   uv run python -m training.train_detector                      # yolo26n.pt, 100 epoch
   uv run python -m training.train_detector --model yolo26s.pt   # model lebih besar
   ```

   Hasil: `models/detector/best.pt`, `reports/detector_training.json`.
4. Evaluasi pada data uji (mAP50, mAP50-95, IoU, precision, recall):

   ```bash
   uv run python -m training.evaluate_detector
   uv run python -m training.evaluate_detector --multi-object    # + data/multi_object_test
   ```

### Navigasi (A* vs Dijkstra)

```bash
uv run python -m scripts.commands run evaluate_navigation --random 100 --center -6.1754 106.8272 --radius 3000 --network-type walk
uv run python -m scripts.commands run evaluate_navigation --pairs data/geo/evaluation_pairs.csv --network-type drive
```

Hasil: `reports/navigation_comparison_<network_type>.{csv,json}`.

## Tes dan kualitas kode

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```
