import os

def default(var_name, value):
    if var_name in os.environ:
        return os.environ[var_name]

    return value


GOOGLE_CLOUD_PROJECT = default('GOOGLE_CLOUD_PROJECT', '')
GOOGLE_DATASTORE_KIND = default('GOOGLE_DATASTORE_KIND', '')
