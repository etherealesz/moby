import sys
import os
import asyncio

# Pastikan folder src masuk ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.bootstrap import bootstrap_runtime, bootstrap_shutdown
from container.factory import create_command_injector
from commands.import_osm import execute


async def main():
    bootstrap_runtime()
    injector = create_command_injector()
    try:
        await execute(injector, args=sys.argv[1:])
    finally:
        await bootstrap_shutdown(injector=injector)


if __name__ == "__main__":
    asyncio.run(main())
