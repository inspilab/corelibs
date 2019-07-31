import json
from datetime import datetime
from django.utils.timezone import utc

from google.cloud import bigtable
from google.cloud.bigtable import column_family
from google.cloud.bigtable import row_filters
from raven.contrib.django.raven_compat.models import client
from django.conf import settings
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from rest_framework.renderers import JSONRenderer
from .constants import (
    GOOGLE_CLOUD_PROJECT, GOOGLE_BIGTABLE_INSTANCE,
    GOOGLE_BIGTABLE_TABLE, GOOGLE_BIGTABLE_COLUMN_FAMILY
)


class Logging(object):

    def __init__(self):
        self._project_id = GOOGLE_CLOUD_PROJECT
        self._instance_id = GOOGLE_BIGTABLE_INSTANCE
        self._table_id = GOOGLE_BIGTABLE_TABLE
        self._column_family_id = GOOGLE_BIGTABLE_COLUMN_FAMILY
        self._columns = [
            'action_time',
            'user_id',
            'content_type',
            'object_id',
            'action_flag',
            'data'
        ]
        self._table = self._get_table()

    def _get_table(self):
        # Create table
        client = bigtable.Client(project=self._project_id, admin=True)
        instance = client.instance(self._instance_id)
        table = instance.table(self._table_id)

        max_versions_rule = column_family.MaxVersionsGCRule(2)
        column_families = {self._column_family_id: max_versions_rule}
        if not table.exists():
            table.create(column_families=column_families)

        return table

    def send_log(self, data):
        timestamp = datetime.utcnow()
        rows = []
        row_key = '%s#%s' % (self._table_id, str(int(datetime.timestamp(timestamp))))
        row_key = row_key.encode()

        if len(data.items()) > 0:
            try:
                for key, value in data.items():
                    column = key
                    row = self._table.row(row_key)
                    row.set_cell(self._column_family_id,
                                column,
                                str(value).encode(),
                                timestamp=timestamp)
                    rows.append(row)

                self._table.mutate_rows(rows)
            except Exception as e:
                client.captureException(
                    "Cannot write log to table %s: Error: %s" % (self._table_id, str(e))
                )

    def get_log(self, **kwargs):
        chains = []
        for k, v in kwargs.items():
            col = row_filters.ColumnQualifierRegexFilter(k.encode())
            label = row_filters.ApplyLabelFilter(v)
            chain = row_filters.RowFilterChain(filters=[col, label])
            chains.append(chain)

        table = self._table
        if len(chains) >= 2:
            row_filter = row_filters.RowFilterUnion(filters=chains)
            partial_rows = table.read_rows(filter_=row_filter)
        else:
            partial_rows = table.read_rows()

        results = []
        for row in partial_rows:
            columns = row.cells[self._column_family_id].keys()
            row_data = {}
            for column in columns:
                cell = row.cells[self._column_family_id][column][0]
                row_data[str(column.decode('utf-8'))] = cell.value.decode('utf-8')

            results.append(row_data)

        return results
