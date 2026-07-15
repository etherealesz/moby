from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

FILES_DIR = PROJECT_ROOT / "files"
CONFIG_FILES_DIR = FILES_DIR / "config"
GOOGLE_SERVICE_ACCOUNT_FILES_DIR = FILES_DIR / "google_service_account"

NAMESPACE_FILEPATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace")
