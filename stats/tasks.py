from celery import shared_task
from users.models import User
from account.models import Account
from stats.views import StatisticsView


@shared_task
def fetch_and_save_statistics():
    try:
        # Извлекаем все account_id из базы данных
        accounts = Account.objects.all()
        account_ids = [account.account_id for account in accounts]

        # Проход по каждому account_id и вызов метода post вашего StatisticsView
        for account_id in account_ids:
            request = None  # Вместо request можно передать нужные параметры запроса, если нужно
            user_id = User.user_id  # Здесь укажите нужные значения
            view = StatisticsView()
            response_stats = view.post(request, user_id, account_id)

            # Обработка ответа, если это необходимо
            if response_stats.status_code == 200:
                print(f"Statistics saved successfully for account_id: {account_id}")
            else:
                print(f"Failed to save statistics for account_id: {account_id}."
                      f" Status code: {response_stats.status_code}")

        return {'success': True, 'message': 'Ads and Statistics saved successfully for all accounts.'}

    except Exception as e:
        # Обработка любых исключений
        return {'error': f"An error occurred: {str(e)}"}
