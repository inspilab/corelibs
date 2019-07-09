import requests
import json
from requests.exceptions import HTTPError
from .constants import CMS_API_URL


class LocationBreadcrumRequest:
    @classmethod
    def location_breadcrum_url(cls, location_code):
        url = "%s/api/location-pages/%s/breadcrum" % (
            CMS_API_URL, location_code
        )
        return url

    @classmethod
    def get_breadcrum(cls, location_code):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = cls.location_breadcrum_url(location_code)
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response
