import unittest
import requests
from mock import patch, Mock
from requests.exceptions import HTTPError, ConnectionError

from corelibs.inspitrip.services.product import Product


class TestPriceEngine(unittest.TestCase):

    def setUp(self):
        self.request_data = {
            'units': [
                {
                    'unit': 1,
                    'quantity': 2
                },
            ],
            'extra_services': [
                {
                    'extra_service': 1,
                    'quantity': 2
                }
            ],
            'start_date': '2019-01-01',
            'end_date': '2019-01-01'
        }

        self.response_data = {
            'units': [
                {
                    'unit': 1,
                    'quantity': 2,
                    'price': 200
                },
            ],
            'extra_services': [
                {
                    'extra_service': 1,
                    'quantity': 2,
                    'price': 200
                }
            ],
            'start_date': '2019-01-01',
            'end_date': '2019-01-01',
            'total': 400
        }

    @patch('requests.post')
    def test_get_price(self, mock_post):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 200
        mock_resp.json = lambda : self.response_data
        mock_post.return_value = mock_resp

        # Send request
        response = Product.get_price(product_pk=123, variant_pk=456, data=self.request_data)
        self.assertEqual(response, self.response_data)

    @patch('requests.post')
    def test_get_price_bad_request(self, mock_post):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 400
        mock_post.return_value = mock_resp

        # Send request
        with self.assertRaises(HTTPError) as context:
            response = Product.get_price(product_pk=123, variant_pk=456, data=self.request_data)

    @patch('requests.post')
    def test_get_price_connection_error(self, mock_post):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 500
        mock_post.return_value = mock_resp

        # Send request
        with self.assertRaises(HTTPError) as context:
            response = Product.get_price(product_pk=123, variant_pk=456, data=self.request_data)
