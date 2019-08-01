from raven.contrib.django.raven_compat.models import client

from corelibs.pubsub import Publisher
from .constants import GOOGLE_PUBSUB_LOG_TOPIC
from corelibs.log.serializers import LogSerializer


def publish_log_data(data):
    try:
        serializer = LogSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        publisher = Publisher(GOOGLE_PUBSUB_LOG_TOPIC)
        publisher.publish(serializer.data)
        return True
    except Exception as e:
        print(e)
        client.captureException()

    return False
