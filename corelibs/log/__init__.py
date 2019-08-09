import json
from datetime import datetime
from django.utils.timezone import utc

from google.cloud import datastore
from raven.contrib.django.raven_compat.models import client
from django.conf import settings
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from rest_framework.renderers import JSONRenderer
from .constants import (
    GOOGLE_CLOUD_PROJECT, GOOGLE_DATASTORE_KIND, LOG_LIMIT
)


class Logging(object):

    def __init__(self):
        self._project_id = GOOGLE_CLOUD_PROJECT
        self._kind = GOOGLE_DATASTORE_KIND
        self._client = datastore.Client()
        self._limit = LOG_LIMIT

    def send_log(self, data):
        timestamp = str(int(datetime.timestamp(datetime.utcnow())))
        task_key = self._client.key(self._kind, timestamp)
        task = datastore.Entity(key=task_key)

        if not data or len(data.items()) == 0:
            return False

        for key, value in data.items():
            task[str(key)] = str(value)

        try:
            self._client.put(task)
            return True
        except Exception as e:
            client.captureException("Cannot push log to datastore. Error: %s" % str(e))

        return False

    def get_log(self, filters=None, page=None):
        query = self._client.query(kind=self._kind, order=('-action_time',))

        if filters:
            for item in filters:
                field, operator, value = item.get('field'), item.get('operator'), item.get('value')
                if field and operator and value:
                    query.add_filter(item.get('field'), item.get('operator'), item.get('value'))

        try:
            if page:
                offset = (int(page) - 1) * self._limit
                results = list(query.fetch(limit=self._limit, offset=offset))
            else:
                results = list(query.fetch())

            return results
        except Exception as e:
            client.captureException("Cannot fetch log from datastore. Error: %s" % str(e))

        return []
