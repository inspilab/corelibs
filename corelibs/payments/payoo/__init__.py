from __future__ import unicode_literals
try:
    # For Python 3.0 and later
    from urllib.error import URLError
    from urllib.parse import urlencode, quote_plus
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import URLError
    from urllib import urlencode, quote_plus
from django.http import HttpResponseRedirect

import xmltodict
import base64
from datetime import datetime, timedelta
import logging
import requests
import json
import hashlib

from .adapter import PayooAdapter
from .validate import ValidateProvider
from .. import PaymentError, PaymentStatus, RedirectNeeded
from ..core import BasicProvider


logger = logging.getLogger(__name__)


class PayooProvider(BasicProvider, ValidateProvider, PayooAdapter):
    '''
    Payoo payment provider
    '''
    def __init__(
            self, secret_key, username, shop_id, shop_title, shop_domain,
            check_out_url, api_user_name, api_password, api_signature,
            order_ship_days, method_default,
            **kwargs
        ):
        self.secret_key = secret_key
        self.username = username
        self.shop_id = shop_id
        self.shop_title = shop_title
        self.shop_domain = shop_domain
        self.check_out_url = check_out_url
        self.api_user_name = api_user_name
        self.api_password = api_password
        self.api_signature = api_signature
        self.order_ship_days = int(order_ship_days or 1)
        self.method_default = method_default or 'bank-payment'
        super(PayooProvider, self).__init__(**kwargs)

    def on_waiting(self, payment, data=None):
        if not payment.id:
            payment.save()

        redirected_to_url = self._get_link_payment(payment)
        if not redirected_to_url:
            payment = self._create_payment(payment, extra_data=data)
            redirected_to_url = self._get_link_payment(payment)

        if not redirected_to_url:
            raise PaymentError("Cannot create payment with payoo method")

        payment.change_status(PaymentStatus.WAITING)
        raise RedirectNeeded(redirected_to_url)

    def transform_data(self, request):
        raise NotImplementedError()

    def process(self, payment, data):
        raise NotImplementedError()

    def capture(self, payment, amount=None):
        pass

    def release(self, payment):
        pass

    def refund(self, payment, amount=None):
        return amount or 0
