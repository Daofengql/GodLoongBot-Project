import contextlib
import functools
import time
from datetime import datetime

from loguru import logger

from library.orm import orm
from library.orm.table import ProcessTime


def process_time(function_name: str):
    """Define a decorator to calculate the time of a function"""

    def decorate(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                total_time = time.perf_counter() - start_time
                with contextlib.suppress(Exception):
                    logger.success(f"{function_name} took {total_time:.2f} seconds")
                    await orm.add(
                        ProcessTime,
                        {
                            "time": datetime.now(),
                            "process_time": total_time,
                            "function": function_name,
                        },
                    )

        return wrapper

    return decorate
