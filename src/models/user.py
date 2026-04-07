from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid import uuid4

class Seller(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        db_table='sellers'