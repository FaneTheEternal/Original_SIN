import uuid

from django.db import models


class GlobalIdentityMixin(models.Model):
    guid = models.UUIDField(
        verbose_name='Code',
        db_index=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True
