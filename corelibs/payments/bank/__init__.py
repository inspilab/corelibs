from __future__ import unicode_literals
try:
    # For Python 3.0 and later
    from urllib.error import URLError
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import URLError
    from urllib import urlencode
from django.http import HttpResponseRedirect

import json
from .. import PaymentError, PaymentStatus, RedirectNeeded
from ..core import BasicProvider
from .validate import ValidateProvider


class BankProvider(BasicProvider, ValidateProvider):
    '''
    Bank payment provider
    '''
    def __init__(self, **kwargs):
        super(BankProvider, self).__init__(**kwargs)

    def transform_data(self, request, option=None):
        data = request.data.copy()
        return data

    def on_waiting(self, payment, data=None):
        payment.change_status(PaymentStatus.WAITING)
        return True

    def process(self, payment, data):
        self._validate_process(payment)

        success_url = payment.get_success_url()
        payment.change_status(PaymentStatus.PREAUTH)
        payment.attrs.bank = json.dumps(data['bank'])
        return success_url

    def capture(self, payment, amount=None):
        self._validate_capture(payment)

        amount = int(amount or payment.total) * int(self._coefficient)
        payment.change_status(PaymentStatus.CONFIRMED)
        return amount

    def release(self, payment):
        return None

    def refund(self, payment, amount=None):
        return amount or 0
