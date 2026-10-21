import argparse
import csv
import html
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import osmnx as ox
from injector import Injector
from shapely.geometry import Point
from shapely.prepared import prep

from core.constants.paths import DATA_DIR, PROJECT_ROOT, REPORTS_DIR
from core.enums.facility_type import EFacilityType
from core.logger.factory import create_app_logger
from core.utils.geo_helper import haversine_distance

logger = create_app_logger()

DEFAULT_SOURCE_DIR = DATA_DIR / "raw" / "sipsn_2025"
DEFAULT_OUTPUT_CSV = DATA_DIR / "geo" / "facilities.csv"


SOURCE_TYPE_MAPPING: dict[str, dict[str, EFacilityType]] = {
    "bank_sampah.txt": {
        "BSU": EFacilityType.BANK_SAMPAH,
        "BSI": EFacilityType.BANK_SAMPAH,
    },
    "tps3r.txt": {
        "TPS 3R / UPS": EFacilityType.TPS3R,
        "TPST (diluar TPA)": EFacilityType.TPST,
    },
    "tpatpst.txt": {
        "TPA Regional": EFacilityType.TPA,
        "TPA Pemda (Non Regional)": EFacilityType.TPA,
    },
}

CITY_BOUNDARIES: dict[str, str] = {
    "Kota Adm. Jakarta Pusat": "Jakarta Pusat, DKI Jakarta, Indonesia",
    "Kota Adm. Jakarta Utara": "Jakarta Utara, DKI Jakarta, Indonesia",
    "Kota Adm. Jakarta Barat": "Jakarta Barat, DKI Jakarta, Indonesia",
    "Kota Adm. Jakarta Selatan": "Jakarta Selatan, DKI Jakarta, Indonesia",
    "Kota Adm. Jakarta Timur": "Jakarta Timur, DKI Jakarta, Indonesia",
    "Kota Tangerang": "Kota Tangerang, Banten, Indonesia",
    "Kota Depok": "Kota Depok, Jawa Barat, Indonesia",
    "Kota Bekasi": "Kota Bekasi, Jawa Barat, Indonesia",
}

VALID_SOURCE_CITIES = {*CITY_BOUNDARIES, "Kab. Adm. Kep. Seribu"}

DUPLICATE_NAME_RADIUS_METER = 1000.0
DUPLICATE_NAME_RADIUS_LANDFILL_METER = 3000.0
EMPTY_VALUES = {"", "-", "0", "null", "none", "n/a"}

CSV_COLUMNS = [
    "facility_id",
    "facility_name",
    "facility_type",
    "latitude",
    "longitude",
    "address",
    "city",
    "jenis_sumber",
    "kota_sumber",
    "sumber",
]


async def execute(injector: Injector, args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="clean_facilities")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_CSV)
    options = parser.parse_args(args or [])

    source_dir = _resolve(options.source)
    output_csv = _resolve(options.output)

    dropped: Counter[str] = Counter()
    raw_counts: dict[str, int] = {}
    rows: list[dict] = []
    for filename, type_mapping in SOURCE_TYPE_MAPPING.items():
        markers = _read_markers(source_dir / filename)
        raw_counts[filename] = len(markers)
        for marker in markers:
            row = _parse_marker(marker, filename, type_mapping)
            if isinstance(row, str):
                dropped[row] += 1
            else:
                rows.append(row)

    boundaries = _load_city_boundaries()
    in_area: list[dict] = []
    for row in rows:
        city = _find_city(boundaries, row["latitude"], row["longitude"])
        if city is None:
            dropped["di_luar_wilayah_studi"] += 1
            continue
        row["city"] = city
        in_area.append(row)

    facilities, duplicate_counts = _deduplicate(in_area)
    dropped.update(duplicate_counts)

    facilities.sort(
        key=lambda r: (
            list(EFacilityType).index(r["facility_type"]),
            r["city"],
            r["facility_name"].lower(),
        )
    )
    for facility_id, row in enumerate(facilities, start=1):
        row["facility_id"] = facility_id

    _write_csv(output_csv, facilities)
    report_path = _write_report(source_dir, output_csv, raw_counts, dropped, facilities)

    logger.info(f"{len(facilities)} fasilitas ditulis ke {output_csv}")
    logger.info(f"Laporan pembersihan: {report_path}")


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def _read_markers(path: Path) -> list[tuple[list, str]]:
    with open(path, encoding="utf-8") as file:
        payload = json.load(file)
    return list(zip(payload["markers"], payload["infowin"], strict=True))


def _parse_marker(
    marker: tuple[list, str],
    filename: str,
    type_mapping: dict[str, EFacilityType],
) -> dict | str:
    values, infowin = marker
    name, latitude, longitude, _, source_type = values[:5]

    facility_type = type_mapping.get(source_type)
    if facility_type is None:
        return "jenis_tidak_dipakai"

    try:
        lat, lon = float(latitude), float(longitude)
    except (TypeError, ValueError):
        return "koordinat_kosong"
    if lat == 0 or lon == 0 or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return "koordinat_tidak_valid"

    facility_name = _tidy_name(_clean_text(name))
    if not facility_name:
        return "nama_kosong"

    # TPA Regional DKI (Bantargebang) tercatat dengan nama TPST
    if facility_type == EFacilityType.TPA and facility_name.upper().startswith("TPST"):
        facility_type = EFacilityType.TPST

    address, source_city = _parse_infowin(infowin)
    if source_city not in VALID_SOURCE_CITIES:
        return "kota_sumber_di_luar_wilayah_studi"

    return {
        "facility_name": facility_name[:100],
        "facility_type": facility_type,
        "latitude": round(lat, 7),
        "longitude": round(lon, 7),
        "address": address[:200] if address else "",
        "jenis_sumber": source_type,
        "kota_sumber": source_city,
        "sumber": filename,
    }


def _parse_infowin(infowin: list[str]) -> tuple[str | None, str]:
    lines = [
        _clean_text(re.sub(r"<[^>]+>", "", part)) or ""
        for part in "".join(infowin).split("<br>")
    ]
    lat_index = next(
        (i for i, line in enumerate(lines) if line.startswith("Lat:")), len(lines)
    )
    city_line = lines[lat_index - 1] if lat_index >= 1 else ""
    source_city = city_line.split(",")[0].strip()
    address = lines[lat_index - 2] if lat_index >= 3 else None
    return address, source_city


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", html.unescape(value)).strip(" ,.;")
    return None if text.lower() in EMPTY_VALUES else text


def _tidy_name(name: str | None) -> str | None:
    if not name or not name.isupper():
        return name
    # singkatan pendek (RW, SDN, TPS, BSU) tetap huruf kapital
    return " ".join(
        word if len(word) <= 3 else word.capitalize() for word in name.split(" ")
    )


def _load_city_boundaries() -> list[tuple[str, object]]:
    ox.settings.use_cache = False
    boundaries = []
    for city, query in CITY_BOUNDARIES.items():
        geometry = ox.geocode_to_gdf(query).geometry.iloc[0]
        boundaries.append((city, prep(geometry)))
    return boundaries


def _find_city(
    boundaries: list[tuple[str, object]], latitude: float, longitude: float
) -> str | None:
    point = Point(longitude, latitude)
    return next((city for city, shape in boundaries if shape.contains(point)), None)


def _name_key(row: dict) -> str:
    key = re.sub(r"[^a-z0-9]", "", row["facility_name"].lower())
    if row["facility_type"] in (EFacilityType.TPA, EFacilityType.TPST):
        key = re.sub(r"^(tpst|tpa)", "", key)
    return key


def _deduplicate(rows: list[dict]) -> tuple[list[dict], Counter[str]]:
    counts: Counter[str] = Counter()
    kept: list[dict] = []
    for row in rows:
        group = row["facility_type"] in (EFacilityType.TPA, EFacilityType.TPST)
        radius = (
            DUPLICATE_NAME_RADIUS_LANDFILL_METER if group else DUPLICATE_NAME_RADIUS_METER
        )
        duplicate_reason = None
        for other in kept:
            same_group = (
                other["facility_type"] == row["facility_type"]
                or group
                and other["facility_type"] in (EFacilityType.TPA, EFacilityType.TPST)
            )
            if not same_group:
                continue
            if (other["latitude"], other["longitude"]) == (
                row["latitude"],
                row["longitude"],
            ) and _name_key(other) == _name_key(row):
                duplicate_reason = "duplikat_persis"
                break
            if _name_key(other) == _name_key(row) and (
                haversine_distance(
                    other["latitude"],
                    other["longitude"],
                    row["latitude"],
                    row["longitude"],
                )
                <= radius
            ):
                duplicate_reason = "duplikat_nama_berdekatan"
                if not other["address"] and row["address"]:
                    other["address"] = row["address"]
                break
        if duplicate_reason:
            counts[duplicate_reason] += 1
        else:
            kept.append(row)
    return kept, counts


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in CSV_COLUMNS})


def _write_report(
    source_dir: Path,
    output_csv: Path,
    raw_counts: dict[str, int],
    dropped: Counter[str],
    facilities: list[dict],
) -> Path:
    report = {
        "dibuat": datetime.now().isoformat(timespec="seconds"),
        "sumber": str(source_dir),
        "keluaran": str(output_csv),
        "jumlah_mentah": raw_counts,
        "dibuang": dict(sorted(dropped.items())),
        "jumlah_bersih": len(facilities),
        "per_tipe": dict(Counter(str(r["facility_type"]) for r in facilities)),
        "per_kota": dict(sorted(Counter(r["city"] for r in facilities).items())),
        "per_kota_tipe": {
            city: dict(
                Counter(str(r["facility_type"]) for r in facilities if r["city"] == city)
            )
            for city in CITY_BOUNDARIES
        },
        "kota_sumber_berbeda": sum(r["kota_sumber"] != r["city"] for r in facilities),
    }
    report_dir = REPORTS_DIR / "fasilitas"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "clean_facilities.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), "utf-8")
    return report_path
