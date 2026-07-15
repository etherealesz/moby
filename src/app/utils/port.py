import sys

from core.constants.server import DEFAULT_SERVER_PORT

PORT_ARGUMENTS = ["--port", "-p"]


def get_server_port():
    """
    Get the server port from command line arguments or return the default port.

    Returns:
        int: The server port number.
    """

    for idx, arg in enumerate(sys.argv):
        if arg in PORT_ARGUMENTS and idx + 1 < len(sys.argv):
            try:
                return int(sys.argv[idx + 1])
            except ValueError:
                pass

        if arg.startswith("--port="):
            try:
                return int(arg.split("=")[1])
            except ValueError:
                pass

    return DEFAULT_SERVER_PORT
