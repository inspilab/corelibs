from django.conf import settings

def default(var_name, value):
    if hasattr(settings, var_name):
        return getattr(settings, var_name)
    return value


GOOGLE_CLOUD_PROJECT = default('GOOGLE_CLOUD_PROJECT', '')
GOOGLE_PUBSUB_TOPIC_DEAD_LETTER = default('GOOGLE_PUBSUB_TOPIC_DEAD_LETTER', '')
FAIL_LIMIT = int(default('FAIL_LIMIT', '5'))
REDIS_HOST = default('REDIS_HOST', '127.0.0.1')
REDIS_PORT = default('REDIS_PORT', '6379')
