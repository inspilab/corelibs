import os

def default(var_name, value):
    if var_name in os.environ:
        return os.environ[var_name]

    return value


LOGGING_HISTORY_MODEL = default('LOGGING_HISTORY_MODEL', False)

ACTION_DELETE = 'DELETE'
ACTION_CREATE = 'CREATE'
ACTION_UPDATE = 'UPDATE'
ACTION_NOTE = 'NOTE'
IGNORE_FIELDS = ['created', 'modified']

LANGUAGE_FALLBACK = 'en'
COUNTRY_FALLBACK = ''
CURRENCY_FALLBACK = 'USD'

USER_ATTR_NAME = default('USER_ATTR_NAME', '_current_user')
