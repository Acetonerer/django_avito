from django.db import models

from users.managers import UserManager


class User(models.Model):
    user_id = models.IntegerField(unique=True, default=0)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "user_id"
    is_anonymous = False
    is_authenticated = True

    objects = UserManager()

    def __str__(self):
        return f"User ID: {self.user_id}"
