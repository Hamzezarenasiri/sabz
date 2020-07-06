from uuid import uuid4

from django.db import models
from django.utils.translation import ugettext_lazy as _

'''
set of custom models to use in apps
'''


class BaseUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, db_index=True)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    # A timestamp representing when this object was created.
    created = models.DateTimeField(verbose_name=_('Creation On'),
                                   auto_now_add=True,
                                   db_index=True,
                                   editable=False)
    # A timestamp reprensenting when this object was last updated.
    updated = models.DateTimeField(verbose_name=_('Modified On'),
                                   auto_now=True,
                                   editable=False)

    class Meta:
        abstract = True
        ordering = ['-created_time', '-updated_time']
