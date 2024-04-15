from django.db import models
from users.models import User


class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    client_id = models.CharField(max_length=100, unique=True)
    client_secret = models.CharField(max_length=100, unique=True)
    account_name = models.CharField(max_length=100)
    user_id = models.IntegerField(default=0)
    access_token = models.CharField(max_length=100)
    refresh_token = models.CharField(max_length=100)
    account_user_id = models.IntegerField(default=0)

    def __str__(self):
        return self.account_name
