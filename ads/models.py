from django.db import models
from account.models import Account


class Ad(models.Model):
    ad_id = models.BigIntegerField(primary_key=True, default=0)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='active')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_user', default=0)

    def __str__(self):
        return f"Ad {self.ad_id} - {self.title}"
