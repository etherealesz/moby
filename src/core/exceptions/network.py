class RequestCancelledError(Exception):
    """
    Exception raised when a client cancels a request before the server can send a response.
    """

    def __init__(self):
        super().__init__("REQUEST_CANCELLED")
