from modules.facilities.models.facility import Facility
from modules.facilities.schemas.facility import SFacilityResponse


def map_facility_to_response(
    facility: Facility,
    include_categories: bool = False,
) -> SFacilityResponse:
    return SFacilityResponse(
        facility_id=facility.facility_id,
        facility_name=facility.facility_name,
        facility_type=facility.facility_type,
        latitude=float(facility.latitude),
        longitude=float(facility.longitude),
        address=facility.address,
        city=facility.city,
        categories=(
            [category.category_name for category in facility.categories]
            if include_categories
            else None
        ),
    )
