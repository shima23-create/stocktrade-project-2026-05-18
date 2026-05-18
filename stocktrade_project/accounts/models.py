from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=1000000)

    def __str__(self):
        return self.username
