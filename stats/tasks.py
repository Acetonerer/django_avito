from celery import shared_task
from account.models import Account
from stats.views import StatisticsView


@shared_task
def fetch_and_save_statistics():
    try:
        # Извлекаем все account_id из базы данных
        accounts = Account.objects.all()

        # Проход по каждому account_id и вызов метода post вашего StatisticsView
        for account in accounts:
            account_id = account.account_id
            user_id = account.user_id  # Здесь укажите нужные значения
            view = StatisticsView()
            response_stats = view.post(user_id, account_id)

            # Обработка ответа, если это необходимо
            if response_stats.status_code == 200:
                print(f"Statistics saved successfully for account_id: {account_id}")
            else:
                print(
                    f"Failed to save statistics for account_id: {account_id}."
                    f" Status code: {response_stats.status_code}"
                )

        return {
            "success": True,
            "message": "Statistics saved successfully for all accounts.",
        }

    except Exception as e:
        # Обработка любых исключений
        return {"error": f"An error occurred: {str(e)}"}
