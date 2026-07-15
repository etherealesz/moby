import logging
import time
from functools import wraps

logger = logging.getLogger()


def debug_exec_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        exec_time = time.perf_counter() - start_time
        logger.debug(f"Execution time of {func.__name__}: {exec_time:.6f} seconds")
        return result

    return wrapper
