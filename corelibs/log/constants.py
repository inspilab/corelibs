import os

def default(var_name, value):
    if var_name in os.environ:
        return os.environ[var_name]

    return value


GOOGLE_CLOUD_PROJECT = default('GOOGLE_CLOUD_PROJECT', '')
GOOGLE_BIGTABLE_INSTANCE = default('GOOGLE_BIGTABLE_INSTANCE', '')
GOOGLE_BIGTABLE_TABLE = default('GOOGLE_BIGTABLE_TABLE', '')
GOOGLE_BIGTABLE_COLUMN_FAMILY = default('GOOGLE_BIGTABLE_COLUMN_FAMILY', '')
