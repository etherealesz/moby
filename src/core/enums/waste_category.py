from enum import StrEnum

from core.constants.waste import WASTE_CATEGORY_LABELS


class EWasteCategory(StrEnum):
    ANORGANIK = "Anorganik"
    B3 = "B3"
    ORGANIK = "Organik"
    RESIDU = "Residu"

    @property
    def label_index(self) -> int:
        return WASTE_CATEGORY_LABELS.index(self.value)

    @property
    def database_value(self) -> int:
        return self.label_index + 1

    @classmethod
    def from_label_index(cls, index: int) -> "EWasteCategory":
        return cls(WASTE_CATEGORY_LABELS[index])

    @classmethod
    def from_database_value(cls, value: int) -> "EWasteCategory | None":
        if 1 <= value <= len(WASTE_CATEGORY_LABELS):
            return cls(WASTE_CATEGORY_LABELS[value - 1])
        return None
