from django.db import models
from users.models import User


class UserRights(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_crm_id = models.CharField(max_length=100)  # Изменено на уникальное поле
    rights = models.CharField(
        max_length=20,
        choices=[("editing", "Editing"), ("view", "View"), ("noaccess", "No Access")],
    )

    def __str__(self):
        return f"{self.user_crm_id} - {self.rights}"
