import os

def default(var_name, value):
    if var_name in os.environ:
        return os.environ[var_name]

    return value


LOGGING_HISTORY_MODEL = default('LOGGING_HISTORY_MODEL', False)
