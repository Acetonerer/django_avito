from django.db import models
from account.models import Account


class Ad(models.Model):
    id = models.IntegerField(default=0, unique=True)
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='active')
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE)

