from functools import wraps
from time import time
from typing import Callable

from utils.logger import global_logger


def timed(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        took_ms = round((time() - start) * 1000, 2)
        if took_ms > 0.01:
            global_logger().info(f"{func.__name__} took {took_ms} ms")
        return result

    return wrapper
