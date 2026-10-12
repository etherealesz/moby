import builtins
import logging
import ssl

from app.factory import create_app
from app.utils.port import get_server_port
from container.factory import create_injector
from core.bootstrap import bootstrap_runtime
from core.config.loader import get_runtime_environment

builtins.ssl = ssl

bootstrap_runtime()

injector = create_injector()
app = create_app(injector=injector)

run_environment = get_runtime_environment()
if run_environment == "uvicorn":
    port = get_server_port()
    logger = logging.getLogger()
    logger.info(f"Server is running on port {port}")
