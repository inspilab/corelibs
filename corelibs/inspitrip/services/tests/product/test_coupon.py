import unittest
import requests
from mock import patch, Mock
from requests.exceptions import HTTPError, ConnectionError

from corelibs.inspitrip.services.product import Product


class TestCoupon(unittest.TestCase):

    def setUp(self):
        pass

    @patch('requests.get')
    def test_get_coupon(self, mock_get):
        pass

    @patch('requests.get')
    def test_get_coupon_bad_request(self, mock_get):
        pass

    @patch('requests.get')
    def test_get_coupon_connection_error(self, mock_get):
        pass
