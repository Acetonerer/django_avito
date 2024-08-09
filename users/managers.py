from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Менеджер для модели пользоватедя
    """

    def create_user(self, user_id):
        if not user_id:
            raise ValueError("User ID is required.")

        user = self.model(user_id=user_id)
        user.save(using=self._db)
        return user
