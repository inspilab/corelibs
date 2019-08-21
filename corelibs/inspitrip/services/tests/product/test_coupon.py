import unittest
import requests
from mock import patch, Mock
from requests.exceptions import HTTPError, ConnectionError

from corelibs.inspitrip.services.product import Product


class TestCoupon(unittest.TestCase):

    def setUp(self):
        self.response_data = {
            'discount_code': 'COUPON20',
            'discount': 50,
            'currency_code': 'USD',
            'language': 'en',
            'country': '',
            'items': [
                {
                    'item': 123,
                    'experience': 189,
                    'discount': 50,
                    'discount_code': 'COUPON20'
                }
            ]
        }

    @patch('requests.put')
    def test_get_coupon(self, mock_get):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 200
        mock_resp.json = lambda : self.response_data
        mock_get.return_value = mock_resp

        # Send request
        response = Product.get_coupon(
            code='COUPON20',
            language='en',
            country='',
            currency_code='USD',
            token='',
            data={}
        )
        self.assertEqual(response, self.response_data)

    @patch('requests.put')
    def test_get_coupon_bad_request(self, mock_get):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        # Send request
        with self.assertRaises(HTTPError) as context:
            response = Product.get_coupon(
                code='COUPON20',
                language='en',
                country='',
                currency_code='USD',
                token='',
                data={}
            )

    @patch('requests.put')
    def test_get_coupon_connection_error(self, mock_get):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp

        # Send request
        with self.assertRaises(HTTPError) as context:
            response = Product.get_coupon(
                code='COUPON20',
                language='en',
                country='',
                currency_code='USD',
                token='',
                data={}
            )
