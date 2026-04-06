from django.db import models
from uuid import uuid4

class Seller(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)