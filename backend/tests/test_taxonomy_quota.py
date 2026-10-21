import pytest
from training.build_dataset import SUBCLASS_ROW, Candidate, select_by_quota
from training.common import SUBCLASSES, TAXONOMY, scaled_quotas


@pytest.mark.parametrize("target", [1500, 1750, 2000])
def test_scaled_quotas_sum_to_target_per_subclass(target):
    quotas = scaled_quotas(target)
    for _, subkelas in SUBCLASSES:
        assert sum(quotas[i.jenis_barang] for i in TAXONOMY if i.subkelas == subkelas) == target


def test_target_2000_equals_design_quota():
    assert scaled_quotas(2000) == {i.jenis_barang: i.kuota for i in TAXONOMY}


def _candidates(counts: dict[str, int]) -> list[Candidate]:
    return [
        Candidate(0, "uji", "", item.jenis_barang, None, md5=f"{item.jenis_barang}-{k}")
        for item in TAXONOMY
        for k in range(counts.get(item.jenis_barang, 2000))
    ]


def test_shortage_covered_by_other_item_in_same_subclass():
    selected, shortages = select_by_quota(_candidates({"roti basi": 500}), 42, 1750)
    assert sum(len(selected[n]) for n in ("nasi", "tulang ayam", "roti basi")) == 1750
    assert not [s for s in shortages if s["jenis_barang"] == SUBCLASS_ROW]


def test_real_subclass_shortage_reported():
    _, shortages = select_by_quota(
        _candidates({"wadah makanan styrofoam": 1000, "styrofoam pelindung kemasan": 30,
                     "gelas styrofoam": 100}),
        42,
        1750,
    )
    row = next(s for s in shortages if s["jenis_barang"] == SUBCLASS_ROW)
    assert (row["subkelas"], row["kurang"]) == ("Styrofoam", 620)


def test_augmentation_fills_train_only(tmp_path, monkeypatch):
    import cv2
    import numpy as np
    from training import build_dataset

    monkeypatch.setattr(build_dataset, "PROJECT_ROOT", tmp_path)
    rows = []
    for k in range(20):
        split = "train" if k < 14 else ("val" if k < 17 else "test")
        path = tmp_path / f"{split}_{k}.jpg"
        cv2.imwrite(str(path), np.full((40, 60, 3), k * 10, dtype=np.uint8))
        rows.append({"path": path.name, "kelas": "Residu", "subkelas": "Styrofoam",
                     "jenis_barang": "gelas styrofoam", "sumber": "uji", "lisensi": "",
                     "split": split, "md5": f"m{k}", "asal": ""})
    augmented = build_dataset.augment_to_target(rows, 25, 42)
    styro = [r for r in augmented if r["subkelas"] == "Styrofoam"]
    assert len(styro) == 5
    assert all(r["split"] == "train" and r["asal"].startswith("train_") for r in styro)


def test_manifest_ignores_report_only_fields(tmp_path, monkeypatch):
    import csv
    from training import build_dataset

    manifest = tmp_path / "manifest.csv"
    monkeypatch.setattr(build_dataset, "MANIFEST_CSV", manifest)
    row = {c: "x" for c in build_dataset.MANIFEST_COLUMNS} | {"operasi": "flip"}
    build_dataset.write_manifest([row])
    assert next(csv.DictReader(open(manifest, encoding="utf-8"))).keys() == set(
        build_dataset.MANIFEST_COLUMNS
    )
