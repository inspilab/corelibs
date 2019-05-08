import os
import redis
import json
import time

from google.cloud import pubsub_v1
from corelibs.pubsub.constants import (
    GOOGLE_CLOUD_PROJECT, GOOGLE_PUBSUB_TOPIC_DEAD_LETTER, FAIL_LIMIT,
    REDIS_HOST, REDIS_PORT
)


class Publisher():

    def __init__(self, topic_name):
        self.topic_name = topic_name
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = 'projects/{project_id}/topics/{topic}'.format(
            project_id=GOOGLE_CLOUD_PROJECT,
            topic=topic_name,
        )

    def publish(self, data):
        print('Publish messages on {}'.format(self.topic_path))
        data = self.handle_data(data)
        message_future = self.publisher.publish(self.topic_path, data=data)
        message_future.add_done_callback(self.callback)
        return message_future.result()

    def callback(self, message_future):
        # When timeout is unspecified, the exception method waits indefinitely.
        if message_future.exception(timeout=30):
            raise Exception(
                'Publishing message on {} threw an Exception {}.'.format(
                    self.topic_path, message_future.exception()
                )
            )
        else:
            print(message_future.result())

    def handle_data(self, data):
        data = json.dumps(data)
        return data.encode('utf-8')
