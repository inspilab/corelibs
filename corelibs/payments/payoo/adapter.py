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

from datetime import datetime, timedelta
import logging
import requests
import json
import hashlib
from .serializers import ResponseSerializer
from .. import PaymentError, PaymentStatus, RedirectNeeded


class PayooAdapter(object):

    def _post(self, payment, *args, **kwargs):
        kwargs['headers'] = {
            'Content-Type': 'application/json',
            'APIUsername': self.api_user_name,
            'APIPassword': self.api_password,
            'APISignature': self.api_signature,
        }
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
        response = requests.post(*args, **kwargs)
        try:
            data = response.json()
        except ValueError:
            data = {}
        if 400 <= response.status_code <= 500:
            self._set_error_data(payment, data)
            message = 'Payoo error'
            error_data = json.dumps(response.json())
            payment.change_status(PaymentStatus.ERROR, message)
            raise PaymentError(error_data)
        else:
            if 'result' in data and data['result'] == 'success':
                self._set_response_data(payment, data)
            else:
                message = 'Payoo error'
                payment.change_status(PaymentStatus.ERROR, message)
                error_data = json.dumps(response.json())
                raise PaymentError(error_data)
        return payment

    def _set_response_data(self, payment, data):
        extra_data = data or {}
        payment.extra_data = json.dumps(extra_data)

    def _set_error_data(self, payment, error):
        extra_data = json.loads(payment.extra_data or '{}')
        extra_data['error'] = error
        payment.extra_data = json.dumps(extra_data)

    def _generate_order_xml_data(self, payment, extra_data):
        order_no = payment.token
        order_cash_amount = int(payment.total)
        order_ship_date = payment.billing_ship_date
        if not order_ship_date:
            order_ship_date = datetime.now().date() + timedelta(days=1)

        order_ship_date = order_ship_date.strftime("%d/%m/%Y")
        order_detail = payment.description
        validity_date = datetime.now() + timedelta(days=self.order_ship_days)
        validity_time = validity_date.strftime("%Y%m%d%H%M%S")
        customer_name = str(payment.billing_first_name) + str(payment.billing_last_name)
        customer_email = payment.billing_email

        order_xml = f'<shops><shop>'
        order_xml += f'<session>{order_no}</session>'
        order_xml += f'<username>{self.username}</username>'
        order_xml += f'<shop_id>{self.shop_id}</shop_id>'
        order_xml += f'<shop_title>{self.shop_title}</shop_title>'
        order_xml += f'<shop_domain>{self.shop_domain}</shop_domain>'
        order_xml += f'<shop_back_url>{self._get_return_url(payment)}</shop_back_url>'
        order_xml += f'<order_no>{order_no}</order_no>'
        order_xml += f'<order_cash_amount>{order_cash_amount}</order_cash_amount>'
        order_xml += f'<order_ship_date>{order_ship_date}</order_ship_date>'
        order_xml += f'<order_ship_days>{self.order_ship_days}</order_ship_days>'
        order_xml += f'<order_description>{quote_plus(order_detail)}</order_description>'
        order_xml += f'<validity_time>{validity_time}</validity_time>'
        order_xml += f'<notify_url>{self.notify_url}</notify_url>'
        order_xml += f'<customer>'
        if (customer_name and customer_email):
            order_xml += f'<name>{customer_name}</name>'
            order_xml += f'<email>{customer_email}</email>'

        order_xml += f'</customer></shop></shops>'

        return order_xml

    def _get_product_data(self, payment, extra_data=None):
        order_xml = self._generate_order_xml_data(payment, extra_data)
        checksum = hashlib.sha512((self.secret_key + order_xml).encode()).hexdigest()

        data = {
            'data': order_xml,
            'checksum': checksum,
            'refer': self.shop_domain,
            'pm': self.method_default
        }
        return data

    def _get_link_payment(self, payment):
        extra_data = json.loads(payment.extra_data or '{}')
        if 'order' in extra_data and extra_data['order'] and 'payment_url' in extra_data['order']:
            return extra_data['order']['payment_url']

        return None

    def _create_payment(self, payment, extra_data=None):
        product_data = self._get_product_data(payment, extra_data)
        payment = self._post(payment, self.check_out_url, data=product_data)
        return payment
