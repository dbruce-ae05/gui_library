import functools
from time import perf_counter, sleep
from uuid import uuid4

from src.gui_library.app_logging import logger


def log_func_with_args(func):
    start = perf_counter()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        funcname = f"{func.__module__}/{func.__qualname__}"
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        uid: str = uuid4().hex
        logger.debug(f"{funcname} called with args {signature}")
        try:
            logger.debug(f"{funcname} START {uid}", extra={"funcname": funcname})
            result = func(*args, **kwargs)
            logger.debug(
                f"{funcname} FINISH {uid} ({(perf_counter() - start): .5f})",
                extra={"funcname": funcname},
            )
            return result
        except Exception as e:
            logger.exception(f"Exception raised in function {funcname}, exception: {str(e)}")
            raise e

    return wrapper


def log_func_time(func):
    start = perf_counter()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        funcname = f"{func.__module__}/{func.__qualname__}"
        try:
            logger.debug(f"{funcname} START")
            result = func(*args, **kwargs)
            logger.debug(
                f"{funcname} FINISH elapsed time: {(perf_counter() - start):.5f}",
                extra={"funcname": funcname},
            )
            return result
        except Exception as e:
            logger.exception(
                f"Exception raised in function {funcname}, exception: {str(e)}",
                extra={"funcname": funcname},
            )
            raise e

    return wrapper


def log_func_start_finish_flags(func):
    start_count = perf_counter()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        funcname = f"{func.__module__}/{func.__qualname__}"
        flag = "".ljust(20, "=")
        start = f"START {funcname}".center(40)
        finish = f"FINISH {funcname}".center(40)
        uid = uuid4().hex
        try:
            logger.info(f"{flag} {start} {flag} {uid=}", extra={"funcname": funcname})
            result = func(*args, **kwargs)
            logger.info(
                f"{flag} {finish} {flag} {uid=} elapsed time: {(perf_counter() - start_count):.5f} seconds",
                extra={"funcname": funcname},
            )

            return result
        except Exception as e:
            logger.exception(f"Exception raised in function {funcname}, exception: {str(e)}")
            raise e

    return wrapper


def retry(func, max_tries: int = 5, wait_time: float = 0.5):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        exceptions_list: list = list()
        while retries < max_tries:
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                exceptions_list.append(e)
                logger.info(
                    f"Retrying function: {func._qualname__}, Retry number: {retries} out of {max_tries}, encountered exception: {e}"
                )
                retries += 1
                sleep(wait_time / 1000)

        raise Exception(
            f"Max retries, ({max_tries}, of function {func} exceeded, exceptions encountered: {exceptions_list}"
        )

    return wrapper
