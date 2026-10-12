import importlib

MASTER_MODEL_MODULES = (
    "modules.waste_categories.models.waste_category",
    "modules.waste_categories.models.waste_subcategory",
    "modules.facilities.models.facility",
    "modules.facilities.models.facility_category",
    "modules.navigation.models.road_node",
    "modules.navigation.models.road_edge",
)


def load_master_models() -> None:
    for module in MASTER_MODEL_MODULES:
        importlib.import_module(module)
