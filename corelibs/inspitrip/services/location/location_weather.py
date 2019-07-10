import requests
import json
from requests.exceptions import HTTPError
from .constants import OPENWEATHER_API_KEY, OPENWEATHER_API_URL


class LocationWeatherRequest:
    @classmethod
    def location_weather_url(cls, lat, lng):
        url = "%s/data/2.5/weather?lat=%s&lon=%s&appid=%s" % (
            OPENWEATHER_API_URL, lat, lng, OPENWEATHER_API_KEY
        )
        return url

    @classmethod
    def get_weather(cls, lat, lng):
        url = cls.location_weather_url(lat, lng)
        try:
            res = requests.get(url)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response
