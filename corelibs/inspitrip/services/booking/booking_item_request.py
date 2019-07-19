import requests
import json
from requests.exceptions import HTTPError
from .constants import BOOKING_API_URL


class BookingItemRequest:
    @classmethod
    def booking_item_url(cls, id):
        url = "%s/api/booking-items/%s" % (
            BOOKING_API_URL, id
        )
        return url

    @classmethod
    def get_booking_item(cls, id, token):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": token
        }
        url = cls.booking_item_url(id)
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response
