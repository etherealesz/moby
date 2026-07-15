from typing import Set

from core.types.environment import ApplicationEnvironment, RuntimeEnvironment

DEVELOPMENT_RUNTIME_ENVIRONMENTS: Set[RuntimeEnvironment] = {"fastapi-dev"}
EXPOSEABLE_API_DOCUMENTATION_APPLICATION_ENVIRONMENTS: Set[ApplicationEnvironment] = {
    "local",
    "development",
    "staging",
}
APPLICATION_ENVIRONMENTS: Set[ApplicationEnvironment] = {
    "local",
    "development",
    "staging",
    "production",
}
