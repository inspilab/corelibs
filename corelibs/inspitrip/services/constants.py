import os

def default(var_name, value):
    if var_name in os.environ:
        return os.environ[var_name]

    return value


PRODUCT_API_URL = default('PRODUCT_API_URL', '127.0.0.1:8000')
