from __future__ import unicode_literals

from datetime import datetime
from django.db import models
from django.conf import settings
from corelibs.middleware import get_current_authenticated_user
from corelibs.log import Logging
from .constants import (
    LOGGING_HISTORY_MODEL, ACTION_DELETE, ACTION_CREATE, ACTION_UPDATE
)


class Mixin(models.Model):

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def _build_log_data(
            self, actor_type, actor, content_type, content_object_id,
            action_flag, extra_data, message
        ):
        actor_name = ''
        if actor and hasattr(actor, 'first_name') and hasattr(actor, 'last_name'):
            actor_name = "%s %s" % (actor.first_name, actor.last_name)
        elif actor and hasattr(actor, 'first_name'):
            actor_name = "%s" % (actor.first_name)

        return {
            'action_time': datetime.now(),
            'actor_type': actor_type,
            'actor_id': actor.id if actor and actor.id else '',
            'actor_email': actor.email if actor and hasattr(actor, 'email') and actor.email else '',
            'actor_name': actor_name,
            'actor_photo': actor.photo if actor and hasattr(actor, 'photo') and actor.photo else '',
            'content_type': content_type,
            'content_object_id': content_object_id if content_object_id else '',
            'action_flag': action_flag,
            'extra_data': extra_data,
            'message': message
        }

    def _log_data(self, action_flag):
        log_data = {}
        extra_data = []
        cls = self.__class__
        user = get_current_authenticated_user()
        if action_flag == ACTION_UPDATE:
            old = cls.objects.get(pk=self.pk)
            new = self
            for field in cls._meta.get_fields():
                field_name = field.name
                try:
                    if getattr(old, field_name) != getattr(new, field_name):
                        extra_data.append(
                            {field_name: str(getattr(new, field_name))}
                        )
                except Exception as e:
                    pass

        log_data = self._build_log_data(
            actor_type='user', actor=user, content_type=cls.__name__,
            content_object_id=self.pk, action_flag=action_flag,
            extra_data=extra_data, message=''
        )
        logging = Logging()
        logging.send_log(log_data)

    def delete(self, *args, **kwargs):
        if settings.LOGGING_HISTORY_MODEL:
            self._log_data(action_flag=ACTION_DELETE)

        super(Mixin, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if settings.LOGGING_HISTORY_MODEL:
            action_flag = ACTION_UPDATE if self.pk else ACTION_CREATE
            self._log_data(action_flag=action_flag)

        super(Mixin, self).save(*args, **kwargs)
