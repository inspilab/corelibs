from __future__ import unicode_literals

from datetime import datetime
from django.db import models
from django.conf import settings
from corelibs.middleware import get_current_authenticated_user
from corelibs.log import Logging
from .constants import (
    GOOGLE_CLOUD_PROJECT, GOOGLE_BIGTABLE_INSTANCE,
    GOOGLE_BIGTABLE_TABLE, GOOGLE_BIGTABLE_COLUMN_FAMILY,
    LOGGING_HISTORY_MODEL
)


class Mixin(models.Model):

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def log_data(self, *args, **kwargs):
        log_data = {}
        if self.pk:
            cls = self.__class__
            old = cls.objects.get(pk=self.pk)
            new = self
            changed_data = []
            for field in cls._meta.get_fields():
                field_name = field.name
                try:
                    if getattr(old, field_name) != getattr(new, field_name):
                        changed_data.append(
                            {field_name: str(getattr(new, field_name))}
                        )
                except Exception as e:
                    pass

            user = get_current_authenticated_user()
            log_data = {
                'action_time': datetime.now(),
                'user_id': user.id if user and user.id else '',
                'user_email': user.email if user and hasattr(user, 'email') and user.email else '',
                'user_first_name': user.first_name if user and hasattr(user, 'first_name') and user.first_name else '',
                'user_last_name': user.last_name if user and hasattr(user, 'last_name') and user.last_name else '',
                'user_photo': user.photo if user and hasattr(user, 'photo') and user.photo else '',
                'content_type': cls.__name__,
                'object_id': self.pk,
                'action_flag': 'UPDATE',
                'data': changed_data
            }
        else:
            cls = self.__class__
            user = get_current_authenticated_user()
            log_data = {
                'action_time': datetime.now(),
                'user_id': user.id if user and user.id else '',
                'user_email': user.email if user and hasattr(user, 'email') and user.email else '',
                'user_first_name': user.first_name if user and hasattr(user, 'first_name') and user.first_name else '',
                'user_last_name': user.last_name if user and hasattr(user, 'last_name') and user.last_name else '',
                'user_photo': user.photo if user and hasattr(user, 'photo') and user.photo else '',
                'content_type': cls.__name__,
                'object_id': '',
                'action_flag': 'CREATE',
                'data': []
            }

        logging = Logging(
            project_id=GOOGLE_CLOUD_PROJECT,
            instance_id=GOOGLE_BIGTABLE_INSTANCE,
            table_id=GOOGLE_BIGTABLE_TABLE,
            column_family_id=GOOGLE_BIGTABLE_COLUMN_FAMILY
        )
        logging.send_log(log_data)

    def save(self, *args, **kwargs):
        if settings.LOGGING_HISTORY_MODEL:
            self.log_data(*args, **kwargs)

        super(Mixin, self).save(*args, **kwargs)
