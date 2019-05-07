import redis
from raven.contrib.django.raven_compat.models import client

from corelibs.pubsub.constants import REDIS_HOST, REDIS_PORT

def calc_wait_time(fail_count):
    # In case you want to wait some arbitrary time before your message "fails"
    return fail_count


def create_key(subscription_path, message_id):
    """
    This helper function creates a unique key for a message
    """
    return "%s_%s" % (subscription_path, message_id)


def get_fail_count(key):
    """
    This function wraps the data store logic. In this case we access redis, but this can be implemented with bigtable, spanner, sql, cassandra, etc.
    Here, I create the client in the function but it can also be created outside.
    """
    try:
        redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        redis_client.incr(key)
        counter = int(redis_client.get(key))
        return counter
    except Exception as e:
        print('Redis error: ', e)
        client.captureException('Redis error: ', e)
