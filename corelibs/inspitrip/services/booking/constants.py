import os

def default(var_name, value):
    if var_name in os.environ:
        return os.environ[var_name]

    return value


BOOKING_API_URL = default('BOOKING_API_URL', 'http://127.0.0.1:8000')
