from enum import StrEnum

from core.enums.waste_category import EWasteCategory


class EFacilityType(StrEnum):
    BANK_SAMPAH = "Bank Sampah"
    TPS3R = "TPS3R"
    TPST = "TPST"
    TPA = "TPA"

    @property
    def accepted_categories(self) -> set[EWasteCategory]:
        return _FACILITY_TYPE_ACCEPTED_CATEGORIES[self]


_FACILITY_TYPE_ACCEPTED_CATEGORIES: dict[EFacilityType, set[EWasteCategory]] = {
    EFacilityType.BANK_SAMPAH: {EWasteCategory.ANORGANIK},
    EFacilityType.TPS3R: {EWasteCategory.ORGANIK},
    EFacilityType.TPST: {EWasteCategory.RESIDU, EWasteCategory.B3},
    EFacilityType.TPA: {EWasteCategory.RESIDU, EWasteCategory.B3},
}
