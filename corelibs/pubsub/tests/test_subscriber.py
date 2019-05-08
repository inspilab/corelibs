import unittest
import mock

from google.cloud import pubsub
from google.cloud import pubsub_v1
from google.auth import credentials

from corelibs.pubsub.subscriber import Subscriber


class ExampleSubscriber(Subscriber):

    def handle_data(self, data):
        return data


class TestSubscriber(unittest.TestCase):

    @mock.patch('corelibs.pubsub.subscriber.pubsub_v1.SubscriberClient')
    def test_subscribe(self, mock_subscriber_client):
        creds = mock.Mock(spec=credentials.Credentials)
        client = pubsub_v1.SubscriberClient(credentials=creds)
        mock_subscriber_client.return_value = client

        data = {
            'foo': 'bar'
        }

        subscriber = ExampleSubscriber('test-subscription')
        subscriber.subscribe()
