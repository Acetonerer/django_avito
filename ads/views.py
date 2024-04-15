from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from account.models import Account


class AdListView(APIView):
    def get(self, request, user_id, account_id):
        """
        Метод получения списка объявлений для заданного аккаунта
        """
        try:
            account = Account.objects.get(user_id=user_id, account_id=account_id)
            access_token = account.access_token

            url = "https://api.avito.ru/core/v1/items"
            headers = {"Authorization": f"Bearer {access_token}"}

            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    items = response.json()
                    return Response({'success': True, 'items': items})
                elif response.status_code == 401:
                    """Пересоздание токена при ошибке 401 (Unauthorized)"""
                    refresh_token, error = self.get_access_token(account.client_id, account.client_secret)

                    if error:
                        return Response({'error': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    # Обновление токена в объекте account
                    account.access_token = refresh_token
                    account.save()

                    # Повторный запрос с обновленным токеном
                    headers = {"Authorization": f"Bearer {refresh_token}"}
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

    def get_access_token(self, client_id, client_secret):
        """
        Метод получения токена доступа Avito
        """
        url = "https://api.avito.ru/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                access_token = response.json().get("access_token")
                return access_token, None
            else:
                return None, f"Error: Unable to retrieve access token. Status code: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return None, f"An error occurred: {e}"


class AdStatisticsView(APIView):
    def post(self, request, user_id, account_id):
        account = Account.objects.get(user_id=user_id, account_id=account_id)
        access_token = account.access_token
        account_user_id = account.account_user_id
        try:
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
            # Формируем URL для запроса
            url = f"https://api.avito.ru/stats/v1/accounts/{account_user_id}/items"

            # Устанавливаем заголовки для авторизации
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # Отправляем POST-запрос к API Avito
            response = requests.post(url, json=data, headers=headers)

            # Обрабатываем ответ от API Avito
            if response.status_code == 200:
                statistics_data = response.json()
                return Response(statistics_data)
            else:
                return Response({'error': f"Failed to fetch statistics data from Avito. "
                                          f"Status code: {response.status_code}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
