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


class ValidateProvider(object):

    def _validate_process(self, payment):
        if payment.status == PaymentStatus.CONFIRMED:
            raise PaymentError('This payment has already been confirmed.')

        if payment.status == PaymentStatus.PREAUTH:
            raise PaymentError('This payment has already been processed.')

        if payment.bid:
            raise PaymentError("Cart #%s has been converted" % payment.cart_id)

        if payment.total <= 0:
            raise PaymentError("Payment total must be greater than 0")

    def _validate_capture(self, payment):
        if payment.status == PaymentStatus.CONFIRMED:
            raise PaymentError('This payment has already been confirmed.')
