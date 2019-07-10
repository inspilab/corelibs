import os

def default(var_name, value):
    if var_name in os.environ:
        return os.environ[var_name]

    return value


CMS_API_URL = default('CMS_API_URL', 'http://127.0.0.1:8000')
OPENWEATHER_API_URL = default('OPENWEATHER_API_URL', 'https://api.openweathermap.org')
OPENWEATHER_API_KEY = default('OPENWEATHER_API_KEY', '')
