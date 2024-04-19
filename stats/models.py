from django.db import models

from account.models import Account
from ads.models import Ad


class Statistics(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateField()
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, default=0)
    uniq_contacts = models.IntegerField(default=0)
    uniq_favorites = models.IntegerField(default=0)
    uniq_views = models.IntegerField(default=0)
