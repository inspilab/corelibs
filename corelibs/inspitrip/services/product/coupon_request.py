import requests
import json
from requests.exceptions import HTTPError
from .constants import PRODUCT_API_URL


class CouponRequest:
    @classmethod
    def coupon_url(cls, code):
        url = "%s/api/coupons/%s" % (
            PRODUCT_API_URL, code
        )
        return url

    @classmethod
    def get_coupon(cls, **kwargs):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": kwargs.get('token'),
            "X-Language": kwargs.get('language'),
            "X-Country": kwargs.get('country'),
            "X-Currency": kwargs.get('currency_code'),
        }
        url = cls.coupon_url(kwargs.get('code'))
        try:
            res = requests.put(url, data=kwargs.get('data'), headers=headers)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response
