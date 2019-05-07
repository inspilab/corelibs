import os
import redis
import json
import time

from google.cloud import pubsub
from raven.contrib.django.raven_compat.models import client
from corelibs.pubsub.constants import (
    GOOGLE_CLOUD_PROJECT, GOOGLE_PUBSUB_TOPIC_DEAD_LETTER, FAIL_LIMIT,
    REDIS_HOST, REDIS_PORT
)


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

class Subscriber():

    def __init__(self, subscription_name):
        self.subscription_name = subscription_name

        # Our subscription
        self.subscription_path = 'projects/{project_id}/subscriptions/{sub}'.format(
            project_id=GOOGLE_CLOUD_PROJECT,
            sub=subscription_name,
        )

        # Our publisher for the dead letter queue
        self.dead_letter_queue_topic = 'projects/{project_id}/topics/{topic}'.format(
            project_id=GOOGLE_CLOUD_PROJECT,
            topic=GOOGLE_PUBSUB_TOPIC_DEAD_LETTER
        )

    def subscribe(self):
        subscriber = pubsub.SubscriberClient()
        subscriber.subscribe(self.subscription_path, callback=self.callback)
        print('Listening for messages on {}'.format(self.subscription_path))

    def callback(self, message):
        try:
            decoded_data = message.data.decode('utf-8')
            result = self.handle_data(data=json.loads(decoded_data))
            message.ack()
            return result
        except Exception as ex:
            self.handle_error(ex, message)

    def handle_data(self, data):
        """
        Handling message from subscription.
        """
        raise NotImplementedError

    def handle_error(self, ex, message):
        """
        Handling errors when there is a failure of handling a message
        """
        key = create_key(self.subscription_path, message.message_id)
        counter = get_fail_count(key)
        if counter >= FAIL_LIMIT:
            print("message %s failed" % message.message_id)
            error_notifier = pubsub.PublisherClient()
            error_notifier.publish(self.dead_letter_queue_topic, message.data, **message.attributes)
            message.ack()
        else:
            wait_time = calc_wait_time(counter)
            time.sleep(wait_time)
            raise ex
