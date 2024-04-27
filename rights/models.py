from django.db import models
from django.contrib.auth.models import User


class UserRights(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_crm_id = models.CharField(max_length=100)
    rights = models.CharField(max_length=20, choices=[('editing', 'Editing'), ('view', 'View'),
                                                      ('noaccess', 'No Access')])

    class Meta:
        unique_together = ('user', 'user_crm_id')
