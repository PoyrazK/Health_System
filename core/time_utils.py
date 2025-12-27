import time

def get_current_time_ms():
    """Returns current time in milliseconds using high-precision perf_counter."""
    return time.perf_counter() * 1000.0
