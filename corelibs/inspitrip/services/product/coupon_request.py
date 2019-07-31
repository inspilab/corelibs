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
    def get_coupon(cls, code, language, country, currency_code):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Language": language,
            "X-Country": country,
            "X-Currency": currency_code,
        }
        url = cls.coupon_url(code)
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response
