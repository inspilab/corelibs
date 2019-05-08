import unittest
import mock

from google.cloud import pubsub_v1
from google.auth import credentials

from corelibs.pubsub.publisher import Publisher


class TestPubscriber(unittest.TestCase):

    @mock.patch('corelibs.pubsub.publisher.pubsub_v1.PublisherClient')
    def test_publish(self, mock_publisher_client):
        creds = mock.Mock(spec=credentials.Credentials)
        client = pubsub_v1.PublisherClient(credentials=creds)
        mock_publisher_client.return_value = client

        data = {
            'foo': 'bar'
        }

        publisher = Publisher('test')
        publisher.publish(data)
