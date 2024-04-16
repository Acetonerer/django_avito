from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from account.models import Account
from account.token import get_new_access_token


class AdListView(APIView):
    def get(self, request, user_id, account_id):
        """
        Метод получения списка объявлений для заданного аккаунта
        """
        try:
            account = get_object_or_404(Account, user_id=user_id, account_id=account_id)
            client_id = account.client_id
            client_secret = account.client_secret

            # Получение нового access_token
            new_access_token, error = get_new_access_token(client_id, client_secret)

            if error:
                return Response({'error': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Обновление токена в объекте account
            account.access_token = new_access_token
            account.save()

            # Повторный запрос с обновленным токеном
            url = "https://api.avito.ru/core/v1/items"
            headers = {"Authorization": f"Bearer {new_access_token}"}

            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    items = response.json()
                    return Response({'success': True, 'items': items})
                else:
                    return Response({
                        'error': f"Failed to retrieve data from Avito with refreshed token."
                                 f" Status code: {response.status_code}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except requests.exceptions.RequestException as e:
                return Response({'error': f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)


class AdStatisticsView(APIView):
    def post(self, request, user_id, account_id):
        try:
            account = get_object_or_404(Account, user_id=user_id, account_id=account_id)
            access_token = account.access_token

            date_from = request.data.get('dateFrom')
            date_to = request.data.get('dateTo')
            fields = request.data.get('fields', [])
            item_ids = request.data.get('itemIds', [])
            period_grouping = request.data.get('periodGrouping')

            data = {
                "dateFrom": date_from,
                "dateTo": date_to,
                "fields": fields,
                "itemIds": item_ids,
                "periodGrouping": period_grouping
            }

            url = f"https://api.avito.ru/stats/v1/accounts/{account.account_user_id}/items"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 403:
                # Пересоздаем access_token
                new_access_token, error = get_new_access_token(account.client_id, account.client_secret)
                if error:
                    return Response({'error': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Обновляем access_token в базе данных
                account.access_token = new_access_token
                account.save()

                # Повторно отправляем запрос с новым access_token
                headers["Authorization"] = f"Bearer {new_access_token}"
                response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                statistics_data = response.json()
                return Response(statistics_data)
            else:
                return Response({'error': f"Failed to retrieve data from Avito. Status code: {response.status_code}"},
                                status=response.status_code)

        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
