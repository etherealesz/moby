from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

FILES_DIR = PROJECT_ROOT / "files"
CONFIG_FILES_DIR = FILES_DIR / "config"

DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_REPORTS_DIR = PROJECT_ROOT / "docs" / "reports"

NAMESPACE_FILEPATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace")
