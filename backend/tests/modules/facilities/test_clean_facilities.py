from commands.clean_facilities import (
    SOURCE_TYPE_MAPPING,
    _deduplicate,
    _parse_infowin,
    _parse_marker,
    _tidy_name,
)
from core.enums.facility_type import EFacilityType

INFOWIN = [
    "<div class=info_content><b>BANK SAMPAH MAWAR</b> (BSU)<br><br>Jl. Melati  No. 1"
    "<br>Kota Adm. Jakarta Pusat, DKI Jakarta<br>Lat: -6.19, Long: 106.87<br></div>"
]


def _marker(name, lat, lon, jenis, infowin=INFOWIN):
    return [name, lat, lon, "icon.png", jenis], infowin


def test_parse_infowin_reads_address_and_city():
    assert _parse_infowin(INFOWIN) == ("Jl. Melati No. 1", "Kota Adm. Jakarta Pusat")


def test_parse_marker_maps_type_and_rejects_others():
    mapping = SOURCE_TYPE_MAPPING["bank_sampah.txt"]
    row = _parse_marker(
        _marker("BANK SAMPAH MAWAR", "-6.19", "106.87", "BSU"), "x", mapping
    )
    assert row["facility_type"] == EFacilityType.BANK_SAMPAH
    assert row["facility_name"] == "Bank Sampah Mawar"

    tps = SOURCE_TYPE_MAPPING["tps3r.txt"]
    assert _parse_marker(_marker("PDU A", "-6.19", "106.87", "PDU"), "x", tps) == (
        "jenis_tidak_dipakai"
    )
    assert _parse_marker(_marker("A", "", "106.87", "BSU"), "x", mapping) == (
        "koordinat_kosong"
    )


def test_parse_marker_rejects_source_city_outside_study_area():
    infowin = [INFOWIN[0].replace("Kota Adm. Jakarta Pusat", "Kab. Karangasem")]
    marker = _marker("Bank Sampah Bali", "-6.20711", "106.79956", "BSU", infowin)
    assert (
        _parse_marker(marker, "x", SOURCE_TYPE_MAPPING["bank_sampah.txt"])
        == "kota_sumber_di_luar_wilayah_studi"
    )


def test_tpst_name_in_tpa_source_becomes_tpst():
    marker = _marker("TPST Bantargebang", "-6.35", "106.98", "TPA Regional")
    row = _parse_marker(marker, "x", SOURCE_TYPE_MAPPING["tpatpst.txt"])
    assert row["facility_type"] == EFacilityType.TPST


def test_tidy_name_keeps_short_acronyms():
    assert _tidy_name("BANK SAMPAH UNIT BERKAH RW 03") == "Bank Sampah Unit Berkah RW 03"
    assert _tidy_name("Bank Sampah ABC") == "Bank Sampah ABC"


def _row(name, lat, lon, facility_type=EFacilityType.BANK_SAMPAH, address=""):
    return {
        "facility_name": name,
        "facility_type": facility_type,
        "latitude": lat,
        "longitude": lon,
        "address": address,
    }


def test_deduplicate_merges_same_name_nearby_only():
    rows = [
        _row("Bank Sampah Mawar", -6.2, 106.8),
        _row("Bank  sampah mawar", -6.2005, 106.8, address="Jl. A"),
        _row("Bank Sampah Mawar", -6.3, 106.8),
        _row("Bank Sampah Melati", -6.2, 106.8),
    ]
    kept, counts = _deduplicate(rows)
    assert len(kept) == 3
    assert kept[0]["address"] == "Jl. A"
    assert counts["duplikat_nama_berdekatan"] == 1


def test_deduplicate_landfill_variants():
    rows = [
        _row("TPST Bantargebang", -6.347938, 106.983037, EFacilityType.TPST),
        _row("TPA Bantar Gebang", -6.348260, 106.997692, EFacilityType.TPA),
    ]
    kept, _ = _deduplicate(rows)
    assert len(kept) == 1
