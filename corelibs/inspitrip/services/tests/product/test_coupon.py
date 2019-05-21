import unittest
import requests
from mock import patch, Mock
from requests.exceptions import HTTPError, ConnectionError

from corelibs.inspitrip.services.product import Product


class TestCoupon(unittest.TestCase):

    def setUp(self):
        self.response_data = {
            'id': 123,
            'code': 'COUPON20',
            'count_by': 'percent',
            'value': 20,
            'currency_code': 'USD',
            'language': 'en',
            'country': '',
            'message': 'Message',
        }

    @patch('requests.get')
    def test_get_coupon(self, mock_get):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 200
        mock_resp.json = lambda : self.response_data
        mock_get.return_value = mock_resp

        # Send request
        response = Product.get_coupon(
            product_pk=123,
            code='COUPON20',
            amount=100,
            language='en',
            country='',
            currency_code='USD'
        )
        self.assertEqual(response, self.response_data)

    @patch('requests.get')
    def test_get_coupon_bad_request(self, mock_get):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        # Send request
        with self.assertRaises(HTTPError) as context:
            response = Product.get_coupon(
                product_pk=123,
                code='COUPON20',
                amount=100,
                language='en',
                country='',
                currency_code='USD'
            )

    @patch('requests.get')
    def test_get_coupon_connection_error(self, mock_get):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp

        # Send request
        with self.assertRaises(HTTPError) as context:
            response = Product.get_coupon(
                product_pk=123,
                code='COUPON20',
                amount=100,
                language='en',
                country='',
                currency_code='USD'
            )
