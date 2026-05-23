from django.db import models
from uuid import uuid4

class InterserviceOutbox(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    queue = models.CharField()
    message = models.JSONField()

    class Meta:
        db_table="interservice_outbox"