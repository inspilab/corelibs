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

import dicttoxml
import re
import xmltodict
import base64
from datetime import datetime, timedelta
import logging
import requests
import json
import hashlib

from .. import PaymentError, PaymentStatus, RedirectNeeded
from . import PayooProvider


class PayooIPNProvider(PayooProvider):

    def transform_data(self, request):
        data = request.data
        product_data = self._validate(data)

        return product_data

    def _validate(self, data):
        # Validate input data
        encoded_product_data = data['Data']

        product_data_xml = base64.b64decode(encoded_product_data).decode('utf-8').replace("\n", "")
        product_data_json = xmltodict.parse(product_data_xml)
        product_data = {}
        for k in product_data_json.keys():
            product_data = product_data_json[k]

        checksum_data = data['Signature']
        keys = data['KeyFields'].split('|')

        str_data = self.secret_key
        for k in keys:
            str_data += ('|' + product_data[k])

        str_hash = hashlib.sha512((str_data).encode()).hexdigest()
        if not str_hash == checksum_data:
            raise PaymentError("Verified is failure. Order No: %s" % product_data['order_no'])

        return product_data

    def _order_data_xml(self, payment):
        order_data_json = self._order_data_json(payment)
        order_data_json['shop']['notify_url'] = self._get_ipn_url(payment)
        order_data_xml = dicttoxml.dicttoxml(order_data_json, attr_type=False, custom_root='shops')
        order_data_xml = re.sub("<\?xml.*?>", "", order_data_xml.decode())
        return order_data_xml

    def process(self, payment, data):
        self._validate_process(payment, data)

        # Process payment
        success_url = payment.get_success_url()
        payment.transaction_id = data['order_no']

        if 'State' in data and data['State'] == 'PAYMENT_RECEIVED':
            payment.captured_amount = payment.total
            payment.change_status(PaymentStatus.CONFIRMED)

        return success_url
