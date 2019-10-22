from __future__ import unicode_literals
try:
    # For Python 3.0 and later
    from urllib.error import URLError
    from urllib.parse import urlencode, quote_plus
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import URLError
    from urllib import urlencode, quote_plus

import dicttoxml
import re

from .serializers import ShopbackSerializer
from .. import PaymentError
from . import PayooProvider


class PayooShopbackProvider(PayooProvider):

    def transform_data(self, request):
        data = request.data.copy()
        self._validate(data)

        return data

    def _validate(self, data):
        new_data = {**data, 'secret_key': self.secret_key}
        serializer = ShopbackSerializer(data=new_data)
        if not serializer.is_valid():
            raise PaymentError(serializer.errors)

    def _order_data_xml(self, payment):
        order_data_json = self._order_data_json(payment)
        order_data_json['shop']['shop_back_url'] = self._get_return_url(payment)
        order_data_xml = dicttoxml.dicttoxml(order_data_json, attr_type=False, custom_root='shops')
        order_data_xml = re.sub("<\?xml.*?>", "", order_data_xml.decode())
        return order_data_xml
