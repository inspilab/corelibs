import os

def default(var_name, value):
    if var_name in os.environ:
        return os.environ[var_name]

    return value


GOOGLE_CLOUD_PROJECT = default('GOOGLE_CLOUD_PROJECT', 'pubsub')
GOOGLE_PUBSUB_TOPIC_DEAD_LETTER = default('GOOGLE_PUBSUB_TOPIC_DEAD_LETTER', 'dead-letters')
FAIL_LIMIT = int(default('FAIL_LIMIT', '5'))
REDIS_HOST = default('REDIS_HOST', '127.0.0.1')
REDIS_PORT = default('REDIS_PORT', '6379')
