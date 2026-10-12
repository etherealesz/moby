import os
import sys

from core.constants.environment import APPLICATION_ENVIRONMENTS
from core.constants.paths import CONFIG_FILES_DIR, NAMESPACE_FILEPATH
from core.types.environment import ApplicationEnvironment, RuntimeEnvironment


def get_environment() -> ApplicationEnvironment:
    if not os.path.exists(NAMESPACE_FILEPATH):
        return "local"

    try:
        with open(NAMESPACE_FILEPATH, "r") as f:
            namespace = f.read().strip()
            if namespace not in APPLICATION_ENVIRONMENTS:
                return "development"
            return namespace
    except Exception:
        return "local"


def get_config_yaml_filepath(environment: ApplicationEnvironment) -> str:
    config_yaml_filepath = CONFIG_FILES_DIR / f"{environment}.yaml"
    return str(config_yaml_filepath)


def get_runtime_environment() -> RuntimeEnvironment:
    cmd = sys.argv[0]

    if "uvicorn" in cmd:
        return "uvicorn"

    if "fastapi" in cmd and not cmd.endswith(".py"):
        if len(sys.argv) == 1:
            return "unknown"

        if sys.argv[1] == "run":
            return "fastapi-run"
        else:
            return "fastapi-dev"

    return "unknown"
