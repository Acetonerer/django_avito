# ads.tasks.py
from celery import shared_task
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
import requests
from account.models import Account
from account.token import get_new_access_token
from ads.models import Ad


@shared_task
def post_fetch_ads(self, request, user_id, account_id):
    try:
        # Находим аккаунт по user_id и account_id
        account = get_object_or_404(Account, user_id=user_id, account_id=account_id)

        # Получаем новый access_token для аккаунта
        new_access_token, error = get_new_access_token(account.client_id, account.client_secret)

        if error:
            return Response({'error': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Обновляем access_token в модели аккаунта
        account.access_token = new_access_token
        account.save()

        # Запрос к Avito для получения списка объявлений
        url = "https://api.avito.ru/core/v1/items"
        headers = {"Authorization": f"Bearer {new_access_token}"}

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                if 'resources' in data:
                    resources = data['resources']

                    # Сохраняем item_ids в базе данных
                    for item in resources:

                        item_id = item['id']
                        if not Ad.objects.filter(ad_id=item_id).exists():
                            # Создаем новую запись в модели Ad
                            Ad.objects.create(ad_id=item_id, title=item.get('title', 'Untitled'), account=account)

                    return Response({'success': True, 'message': 'Items retrieved and saved successfully.'})

                else:
                    return Response({'error': 'No items found in response from Avito'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                return Response({
                    'error': f"Failed to retrieve data from Avito with refreshed token. Status code: {response.status_code}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except requests.exceptions.RequestException as e:
            return Response({'error': f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
