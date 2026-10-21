import argparse
import csv
from pathlib import Path

from injector import Injector
from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert

from core.constants.paths import DATA_DIR, PROJECT_ROOT
from core.constants.waste import WASTE_CATEGORY_LABELS
from core.enums.facility_type import EFacilityType
from core.enums.waste_category import EWasteCategory
from core.logger.factory import create_app_logger
from infrastructures.databases.master import DatabaseMasterSession
from modules.facilities.models.facility import Facility
from modules.facilities.models.facility_category import FacilityCategory
from modules.waste_categories.models.waste_category import WasteCategory
from modules.waste_categories.models.waste_subcategory import WasteSubcategory

logger = create_app_logger()

DEFAULT_FACILITIES_CSV = DATA_DIR / "geo" / "facilities.csv"

WASTE_CATEGORIES: list[dict] = [
    {
        "category_id": EWasteCategory.ANORGANIK.database_value,
        "category_name": EWasteCategory.ANORGANIK.value,
        "category_code": "ANO",
        "description": "Sampah yang sulit terurai dan dapat didaur ulang: plastik, "
        "kertas dan karton, kaca, logam, tekstil.",
    },
    {
        "category_id": EWasteCategory.B3.database_value,
        "category_name": EWasteCategory.B3.value,
        "category_code": "B3",
        "description": "Sampah bahan berbahaya dan beracun rumah tangga: baterai, "
        "elektronik kecil, lampu, kemasan bertekanan.",
    },
    {
        "category_id": EWasteCategory.ORGANIK.database_value,
        "category_name": EWasteCategory.ORGANIK.value,
        "category_code": "ORG",
        "description": "Sampah yang mudah terurai: sisa makanan, kulit buah, sisa "
        "bahan dapur, daun dan ranting.",
    },
    {
        "category_id": EWasteCategory.RESIDU.database_value,
        "category_name": EWasteCategory.RESIDU.value,
        "category_code": "RES",
        "description": "Sampah yang tidak dapat didaur ulang maupun dikompos: "
        "produk sanitasi sekali pakai, saset, styrofoam, puntung rokok.",
    },
]

WASTE_SUBCATEGORIES: list[tuple[EWasteCategory, str, str]] = [
    (EWasteCategory.B3, "Baterai", "Baterai AA/AAA, baterai ponsel/lithium"),
    (EWasteCategory.B3, "Elektronik Kecil", "Kabel, charger, earphone"),
    (EWasteCategory.B3, "Lampu", "Bohlam, LED, neon"),
    (EWasteCategory.B3, "Kemasan Bertekanan", "Kaleng aerosol, korek gas"),
    (
        EWasteCategory.ANORGANIK,
        "Plastik",
        "Botol PET, plastik kresek polos, gelas plastik",
    ),
    (EWasteCategory.ANORGANIK, "Kertas dan Karton", "Kardus, kertas HVS/koran"),
    (EWasteCategory.ANORGANIK, "Kaca", "Botol kaca, pecahan kaca"),
    (EWasteCategory.ANORGANIK, "Logam", "Kaleng minuman, kaleng makanan"),
    (EWasteCategory.ANORGANIK, "Tekstil", "Pakaian bekas, kain perca, kaus kaki"),
    (EWasteCategory.ORGANIK, "Sisa Makanan", "Nasi, tulang ayam"),
    (EWasteCategory.ORGANIK, "Kulit Buah", "Kulit pisang, kulit jeruk, kulit semangka"),
    (
        EWasteCategory.ORGANIK,
        "Sisa Bahan Dapur",
        "Cangkang telur, kulit bawang, kulit wortel, kulit kentang",
    ),
    (EWasteCategory.ORGANIK, "Daun dan Ranting", "Daun kering, ranting, potongan rumput"),
    (
        EWasteCategory.RESIDU,
        "Produk Sanitasi Sekali Pakai",
        "Masker medis, popok, pembalut",
    ),
    (
        EWasteCategory.RESIDU,
        "Kemasan Saset",
        "Bungkus mi instan, saset kopi bubuk, saset sampo/deterjen",
    ),
    (
        EWasteCategory.RESIDU,
        "Styrofoam",
        "Wadah makanan styrofoam, styrofoam pelindung kemasan",
    ),
    (EWasteCategory.RESIDU, "Puntung Rokok", "Puntung rokok"),
]

FACILITY_CSV_COLUMNS = {
    "facility_name",
    "facility_type",
    "latitude",
    "longitude",
    "address",
    "city",
}


async def execute(injector: Injector, args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="seed_database")
    parser.add_argument("--facilities", type=Path, default=DEFAULT_FACILITIES_CSV)
    options = parser.parse_args(args or [])

    session = injector.get(DatabaseMasterSession)
    facilities_csv: Path = options.facilities
    if not facilities_csv.is_absolute():
        facilities_csv = PROJECT_ROOT / facilities_csv

    async with session.begin():
        await _seed_waste_categories(session)
        await _seed_waste_subcategories(session)

        if facilities_csv.exists():
            await _seed_facilities(session, facilities_csv)
        else:
            logger.warning(
                f"{facilities_csv} tidak ditemukan, Facility dan Facility_Category "
                "tidak diisi."
            )


async def _seed_waste_categories(session: DatabaseMasterSession) -> None:
    assert [c["category_name"] for c in WASTE_CATEGORIES] == list(WASTE_CATEGORY_LABELS)

    stmt = insert(WasteCategory).values(WASTE_CATEGORIES)
    stmt = stmt.on_conflict_do_update(
        index_elements=[WasteCategory.category_id],
        set_={
            "category_name": stmt.excluded.category_name,
            "category_code": stmt.excluded.category_code,
            "description": stmt.excluded.description,
            "updated_at": func.current_timestamp(),
        },
    )
    await session.execute(stmt)
    logger.info(f"Waste_Category: {len(WASTE_CATEGORIES)} baris")


async def _seed_waste_subcategories(session: DatabaseMasterSession) -> None:
    rows = [
        {
            "subcategory_id": index,
            "category_id": category.database_value,
            "subcategory_name": name,
            "description": description,
        }
        for index, (category, name, description) in enumerate(
            WASTE_SUBCATEGORIES, start=1
        )
    ]
    stmt = insert(WasteSubcategory).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=[WasteSubcategory.subcategory_id],
        set_={
            "category_id": stmt.excluded.category_id,
            "subcategory_name": stmt.excluded.subcategory_name,
            "description": stmt.excluded.description,
            "updated_at": func.current_timestamp(),
        },
    )
    await session.execute(stmt)
    logger.info(f"Waste_Subcategory: {len(rows)} baris")


async def _seed_facilities(session: DatabaseMasterSession, csv_path: Path) -> None:
    facilities, facility_categories = _read_facilities_csv(csv_path)
    if not facilities:
        logger.warning(f"{csv_path} kosong, Facility tidak diisi.")
        return

    stmt = insert(Facility).values(facilities)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Facility.facility_id],
        set_={
            "facility_name": stmt.excluded.facility_name,
            "facility_type": stmt.excluded.facility_type,
            "latitude": stmt.excluded.latitude,
            "longitude": stmt.excluded.longitude,
            "address": stmt.excluded.address,
            "city": stmt.excluded.city,
            "updated_at": func.current_timestamp(),
        },
    )
    await session.execute(stmt)

    facility_ids = [row["facility_id"] for row in facilities]
    await session.execute(delete(FacilityCategory))
    removed = await session.execute(
        delete(Facility).where(Facility.facility_id.not_in(facility_ids))
    )
    await session.execute(insert(FacilityCategory).values(facility_categories))

    logger.info(
        f"Facility: {len(facilities)} baris ({removed.rowcount} lama dihapus), "
        f"Facility_Category: {len(facility_categories)} baris"
    )


def _read_facilities_csv(csv_path: Path) -> tuple[list[dict], list[dict]]:
    facilities: list[dict] = []
    facility_categories: list[dict] = []

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        missing = FACILITY_CSV_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Kolom wajib tidak ada di {csv_path}: {sorted(missing)}")

        for line_number, row in enumerate(reader, start=2):
            facility_type = EFacilityType(row["facility_type"].strip())
            facility_id = (
                int(row["facility_id"])
                if row.get("facility_id", "").strip()
                else len(facilities) + 1
            )
            latitude = float(row["latitude"])
            longitude = float(row["longitude"])
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError(f"Koordinat tidak valid pada baris {line_number}")

            facilities.append(
                {
                    "facility_id": facility_id,
                    "facility_name": row["facility_name"].strip()[:100],
                    "facility_type": facility_type.value,
                    "latitude": round(latitude, 7),
                    "longitude": round(longitude, 7),
                    "address": (row.get("address") or "").strip()[:200] or None,
                    "city": row["city"].strip()[:50],
                }
            )
            facility_categories.extend(
                {"facility_id": facility_id, "category_id": category.database_value}
                for category in sorted(
                    facility_type.accepted_categories, key=lambda c: c.database_value
                )
            )

    return facilities, facility_categories
