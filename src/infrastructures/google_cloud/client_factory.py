from google.cloud import storage

from core.constants.paths import GOOGLE_SERVICE_ACCOUNT_FILES_DIR
from core.types.environment import ApplicationEnvironment


def create_google_cloud_storage_client(
    environment: ApplicationEnvironment,
) -> storage.Client:
    """
    Create a Google Cloud Storage client using the service account JSON file
    for the specified environment.

    Args:
        environment (ApplicationEnvironment): The application environment (e.g., development, staging, production).

    Returns:
        storage.Client: An instance of the Google Cloud Storage client.
    """

    service_account_json_filepath = (
        GOOGLE_SERVICE_ACCOUNT_FILES_DIR / f"{environment}.json"
    )

    if not service_account_json_filepath.exists():
        service_account_json_filepath = (
            GOOGLE_SERVICE_ACCOUNT_FILES_DIR / "development.json"
        )

    client = storage.Client.from_service_account_json(
        service_account_json_filepath,
    )
    return client
