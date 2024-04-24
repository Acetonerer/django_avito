# ads.tasks.py
from celery import shared_task

from users.models import User
from account.models import Account
from ads.views import AdListView


@shared_task
def fetch_and_save_ads():
    try:
        # Извлекаем все account_id из базы данных
        accounts = Account.objects.all()

        # Проход по каждому account_id и вызов метода post AdListView()
        for account in accounts:
            account_id = account.account_id
            user_id = account.user_id
            view = AdListView()
            response_ads = view.post(user_id, account_id)

            # Обработка ответа, если это необходимо
            if response_ads.status_code == 200:
                print(f"Ads saved successfully for account_id: {account_id}")
            else:
                print(f"Failed to save ads for account_id: {account_id}."
                      f" Status code: {response_ads.status_code}")

    except Exception as e:
        # Обработка любых исключений
        return {'error': f"An error occurred: {str(e)}"}
