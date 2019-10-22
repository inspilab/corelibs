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

from .. import PaymentError, PaymentStatus, RedirectNeeded
from . import PayooProvider


class PayooIPNProvider(PayooProvider):

    def transform_data(self, request):
        data = xmltodict.parse(request.data)
        self._validate(data)

        encoded_product_data = data['PayooConnectionPackage']['Data']
        product_data = base64.b64encode(encoded_product_data.encode('utf-8')).decode('utf-8').replace("\n", "")
        return product_data

    def _validate(self, data):
        # Validate input data
        encoded_product_data = data['PayooConnectionPackage']['Data']

        product_data = base64.b64encode(encoded_product_data.encode('utf-8')).decode('utf-8').replace("\n", "")
        checksum_data = data['PayooConnectionPackage']['Signature']
        keys = data['PayooConnectionPackage']['KeyFields']

        str_data = self.secret_key
        for k in keys:
            str_data += ('|' + product_data[k])

        str_hash = hashlib.sha512((str_data).encode()).hexdigest()
        if not str_hash == checksum:
            raise PaymentError("Verified is failure. Order No: %s" % product_data['order_no'])

        if 'State' in product_data and product_data['State'] != 'PAYMENT_RECEIVED':
            raise PaymentError("Process payoo failed. Error: %s" % product_data['State'])

    def _order_data_xml(self, payment):
        order_data_json = self._order_data_json(payment)
        order_data_json['notify_url'] = self._get_ipn_url(payment)
        order_data_xml = dicttoxml.dicttoxml(order_data_json, attr_type=False, custom_root='shops')
        order_data_xml = re.sub("<\?xml.*?>", "", order_data_xml.decode())
        return order_data_xml
