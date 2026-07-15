import builtins
import logging
import ssl

from app.factory import create_app
from app.utils.port import get_server_port
from container.factory import create_injector
from core.bootstrap import bootstrap_runtime
from core.config.loader import get_runtime_environment

# Sometimes, httpx client that not registered inside container would throw
# error about missing ssl module, so we need to register it globally.
# Removing comment below will cause unclear error message about ssl module when
# httpx client is not registered inside container.
builtins.ssl = ssl  # pyright: ignore

bootstrap_runtime()

injector = create_injector()
app = create_app(injector=injector)

run_environment = get_runtime_environment()
if run_environment == "uvicorn":
    port = get_server_port()
    logger = logging.getLogger()
    logger.info(f"Server is running on port {port}")
