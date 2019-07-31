import os

def default(var_name, value):
    if var_name in os.environ:
        return os.environ[var_name]

    return value


USER_ATTR_NAME = default('USER_ATTR_NAME', '_current_user')
