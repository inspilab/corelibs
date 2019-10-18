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


class BankProvider(BasicProvider):
    '''
    Bank payment provider
    '''
    def __init__(self, **kwargs):
        super(BankProvider, self).__init__(**kwargs)

    def session_start(self, payment, data=None):
        payment.change_status(PaymentStatus.WAITING)
        return True

    def preprocess_data(self, request, option=None):
        data = request.data.copy()
        return data

    def process_data(self, payment, data):
        if payment.status == PaymentStatus.CONFIRMED:
            raise PaymentError('This payment has already been confirmed.')

        if payment.status == PaymentStatus.PREAUTH:
            raise PaymentError('This payment has already been processed.')

        success_url = payment.get_success_url()
        payment.change_status(PaymentStatus.PREAUTH)
        payment.attrs.bank = json.dumps(data['bank'])
        return success_url

    def capture(self, payment, amount=None):
        if payment.status == PaymentStatus.CONFIRMED:
            raise PaymentError('This payment has already been confirmed.')

        # Check supported currencies

        amount = int(amount or payment.total) * int(self._coefficient)
        payment.change_status(PaymentStatus.CONFIRMED)
        return amount

    def release(self, payment):
        return None

    def refund(self, payment, amount=None):
        return amount or 0
