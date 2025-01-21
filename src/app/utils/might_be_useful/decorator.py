import random
import time


def retry(retries=3, exception=Exception, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    attempts += 1
                    print(f"Failed ({attempts}/{retries})")
                    time.sleep(delay)
            raise exception

        return wrapper

    return decorator


import random
import time


def debug(func):
    def wrapper(*args, **kwargs):
        print(f"Calling function {func.__name__} with args {args} and kwargs {kwargs}")
        result = func(*args, **kwargs)
        print(f"Result was {result}")
        return result

    return wrapper


import random
import time


def rate_limiter(calls, period):
    def decorator(func):
        last_calls = []

        def wrapper(*args, **kwargs):
            nonlocal last_calls

            now = time.time()

            last_calls = [
                call_time for call_time in last_calls if now - call_time < period
            ]

            if len(last_calls) > calls:
                raise RuntimeError("Rate limit exceeded. Try again later")

            last_calls.append(now)

            return func(*args, **kwargs)

        return wrapper

    return decorator


import time


def time_logger(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"Time taken: {end-start:.4f}")
        return result

    return wrapper
