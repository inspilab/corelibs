import unittest
import requests
from mock import patch, Mock
from requests.exceptions import HTTPError, ConnectionError

from corelibs.inspitrip.services.product import Product


class TestProduct(unittest.TestCase):

    def setUp(self):
        self.response_data = {
            'id': 189,
            'currency_code': 'USD',
            'language': 'en',
            'country': '',
            'admin_fee': 20,
        }

    @patch('requests.get')
    def test_get_product(self, mock_get):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 200
        mock_resp.json = lambda : self.response_data
        mock_get.return_value = mock_resp

        # Send request
        response = Product.get_detail(
            product_pk=123
        )
        self.assertEqual(response, self.response_data)

    @patch('requests.get')
    def test_get_product_bad_request(self, mock_get):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        # Send request
        with self.assertRaises(HTTPError) as context:
            response = Product.get_detail(
                product_pk=123
            )

    @patch('requests.get')
    def test_get_product_connection_error(self, mock_get):
        # Mock response
        mock_resp = requests.models.Response()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp

        # Send request
        with self.assertRaises(HTTPError) as context:
            response = Product.get_detail(
                product_pk=123
            )
