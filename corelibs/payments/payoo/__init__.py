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
from .serializers import OrderSerializer, ResponseSerializer
from .. import PaymentError, PaymentStatus, RedirectNeeded
from ..core import BasicProvider

logger = logging.getLogger(__name__)


class PayooProvider(BasicProvider):
    '''
    Payoo payment provider
    '''
    def __init__(
            self, secret_key, username, shop_id, shop_title, shop_domain, shop_back_url,
            notify_url, check_out_url, api_user_name, api_password, api_signature,
            order_ship_days,
            **kwargs
        ):
        self.secret_key = secret_key
        self.username = username
        self.shop_id = shop_id
        self.shop_title = shop_title
        self.shop_domain = shop_domain
        self.shop_back_url = shop_back_url
        self.notify_url = notify_url
        self.check_out_url = check_out_url
        self.api_user_name = api_user_name
        self.api_password = api_password
        self.api_signature = api_signature
        self.order_ship_days = int(order_ship_days or 1)
        super(PayooProvider, self).__init__(**kwargs)

    def post(self, payment, *args, **kwargs):
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
            self.set_error_data(payment, data)
            logger.debug(data)
            message = 'Payoo error'
            if response.status_code == 400:
                error_data = response.json()
                logger.warning(message, extra={
                    'response': error_data,
                    'status_code': response.status_code})
                message = error_data.get('message', message)
            else:
                logger.warning(
                    message, extra={'status_code': response.status_code})
            payment.change_status(PaymentStatus.ERROR, message)
            raise PaymentError(message)
        else:
            if 'result' in data and data['result'] != 'success':
                message = data.get('message', message)
                payment.change_status(PaymentStatus.ERROR, message)
                raise PaymentError(message)
            self.set_response_data(payment, data)
        return payment

    def set_response_data(self, payment, data):
        extra_data = data or {}
        payment.extra_data = json.dumps(extra_data)

    def set_error_data(self, payment, error):
        extra_data = json.loads(payment.extra_data or '{}')
        extra_data['error'] = error
        payment.extra_data = json.dumps(extra_data)

    def _generate_order_xml_data(self, payment, extra_data):
        order_no = extra_data['order_no']
        order_cash_amount = extra_data['order_cash_amount']
        order_ship_date = datetime.strptime(extra_data['order_ship_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
        order_detail = extra_data['order_detail']
        validity_date = datetime.now() + timedelta(days=self.order_ship_days)
        validity_time = validity_date.strftime("%Y%m%d%H%M%S")
        customer_name = extra_data['customer_name']
        customer_phone = extra_data['customer_phone']
        customer_email = extra_data['customer_email']

        order_xml = f'<shops><shop>'
        order_xml += f'<session>{order_no}</session>'
        order_xml += f'<username>{self.username}</username>'
        order_xml += f'<shop_id>{self.shop_id}</shop_id>'
        order_xml += f'<shop_title>{self.shop_title}</shop_title>'
        order_xml += f'<shop_domain>{self.shop_domain}</shop_domain>'
        order_xml += f'<shop_back_url>{self.shop_back_url}</shop_back_url>'
        order_xml += f'<order_no>{order_no}</order_no>'
        order_xml += f'<order_cash_amount>{order_cash_amount}</order_cash_amount>'
        order_xml += f'<order_ship_date>{order_ship_date}</order_ship_date>'
        order_xml += f'<order_ship_days>{self.order_ship_days}</order_ship_days>'
        order_xml += f'<order_description>{quote_plus(order_detail)}</order_description>'
        order_xml += f'<validity_time>{validity_time}</validity_time>'
        order_xml += f'<notify_url>{self.notify_url}</notify_url>'
        order_xml += f'<customer><name>{customer_name}</name><phone>{customer_phone}</phone>'
        order_xml += f'<email>{customer_email}</email></customer></shop></shops>'

        return order_xml

    def get_product_data(self, payment, extra_data=None):
        order_xml = self._generate_order_xml_data(payment, extra_data)
        checksum = hashlib.sha512((self.secret_key + order_xml).encode()).hexdigest()

        data = {
            'data': order_xml,
            'checksum': checksum,
            'refer': self.shop_domain
        }
        return data

    def _get_link_payment(self, payment):
        extra_data = json.loads(payment.extra_data or '{}')
        if 'order' in extra_data and extra_data['order'] and 'payment_url' in extra_data['order']:
            return extra_data['order']['payment_url']

        return None

    def get_form(self, payment, data=None):
        # Check coefficient support
        self.get_coefficient(currency_code=payment.currency)
        try:
            serializer = OrderSerializer(data=data)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise PaymentError(str(e))

        if not payment.id:
            payment.save()

        redirected_to_url = self._get_link_payment(payment)
        if not redirected_to_url:
            payment = self.create_payment(payment, extra_data=data)
            redirected_to_url = self._get_link_payment(payment)

        if not redirected_to_url:
            raise PaymentError("Cannot create payment with payoo method")

        payment.change_status(PaymentStatus.WAITING)
        raise RedirectNeeded(redirected_to_url)

    def process_data(self, payment, request):
        # Check coefficient support
        self.get_coefficient(currency_code=payment.currency)

        success_url = payment.get_success_url()
        try:
            # Check format request
            serializer = ResponseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            session = serializer.validated_data['session']
            order_no = serializer.validated_data['order_no']
            status = serializer.validated_data['status']
            checksum = serializer.validated_data['checksum']

            # Checksum
            str_hash = hashlib.sha512(
                (self.secret_key + session + '.' + order_no + '.' + status).encode()
            ).hexdigest()
            if not str_hash == checksum:
                raise Exception("Verified is failure. Order No: %s" % order_no)

            # Check if payment is paid
            if not status == 1:
                if 'errormsg' in request.data and request.data['errormsg']:
                    self.set_error_data(payment, request.data['errormsg'])
                payment.change_status(PaymentStatus.REJECTED)
                return payment.get_failure_url()
        except Exception as e:
            raise PaymentError(str(e))

        # Process payment
        payment.captured_amount = payment.total
        payment.change_status(PaymentStatus.CONFIRMED)
        return success_url

    def create_payment(self, payment, extra_data=None):
        product_data = self.get_product_data(payment, extra_data)
        payment = self.post(payment, self.check_out_url, data=product_data)
        return payment

    def capture(self, payment, amount=None):
        pass

    def release(self, payment):
        pass

    def refund(self, payment, amount=None):
        return amount or 0
