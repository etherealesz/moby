from sqlalchemy import ColumnElement, exists, or_, select

from core.enums.waste_category import EWasteCategory
from modules.facilities.models.facility import Facility
from modules.facilities.models.facility_category import FacilityCategory


def build_get_all_search_clause(search: str) -> ColumnElement:
    clauses = {
        Facility.facility_name.ilike(f"%{search}%"),
        Facility.address.ilike(f"%{search}%"),
    }

    if search.isdigit():
        clauses.add(Facility.facility_id == int(search))

    return or_(*clauses)


def build_accepts_category_clause(category: EWasteCategory) -> ColumnElement:
    return exists(
        select(FacilityCategory.facility_id).where(
            FacilityCategory.facility_id == Facility.facility_id,
            FacilityCategory.category_id == category.database_value,
        )
    )
