from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ads.models import Ad
from ads.views import AdListView
from stats.models import Statistics
from .models import Account
from users.models import User
from .serializers import AccountSerializer
import requests
from account.token import get_access_token


class AccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Post запрос для создания аккаунта
        """
        account_name = request.data.get('account_name')
        user_id = request.data.get('user_id')
        client_id = request.data.get('client_id')
        client_secret = request.data.get('client_secret')

        if not all([account_name, user_id, client_id, client_secret]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        access_token, error = get_access_token(client_id, client_secret)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, user_id=user_id)

        account_user_id, error = self.get_account_user_id(access_token)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.create(
                account_name=account_name,
                user_id=user_id,
                client_id=client_id,
                client_secret=client_secret,
                access_token=access_token,
                account_user_id=account_user_id,
            )

            # Получаем и сохраняем объявления для данного аккаунта
            ad_list_view = AdListView()
            response = ad_list_view.post(user_id, account.account_id)

            if response.status_code != status.HTTP_200_OK:
                return response  # Передаем ответ клиенту в случае ошибки при получении объявлений

            # Добавление статистики за месяц до текущего дня
            date_to = datetime.now().date()
            date_from = date_to - timedelta(days=30)  # Получаем дату 30 дней назад

            stats_list = self.get_statistics_for_month(account, date_from, date_to)

            for stats_date, item_id, stats_entry in stats_list:
                uniq_contacts = stats_entry.get('uniqContacts', 0)
                uniq_favorites = stats_entry.get('uniqFavorites', 0)
                uniq_views = stats_entry.get('uniqViews', 0)

                Statistics.objects.create(
                    account=account,
                    date=stats_date,
                    ad_id=item_id,
                    uniq_contacts=uniq_contacts,
                    uniq_favorites=uniq_favorites,
                    uniq_views=uniq_views
                )

            serializer = AccountSerializer(account)
            response_data = {
                'success': True,
                'account': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_statistics_for_month(self, account, date_from, date_to):
        url = f"https://api.avito.ru/stats/v1/accounts/{account.account_user_id}/items"
        headers = {
            "Authorization": f"Bearer {account.access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat(),
            "fields": ["uniqViews", "uniqContacts", "uniqFavorites"],
            "periodGrouping": "day",
            "itemIds": [ad.ad_id for ad in Ad.objects.filter(account_id=account.account_id)]
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            statistics_data = response.json()

            if 'result' in statistics_data and 'items' in statistics_data['result']:
                items = statistics_data['result']['items']
                stats_list = []

                for item in items:
                    item_id = item['itemId']
                    stats_entry = item.get('stats', [{}])[0]  # Берем первую запись из stats_list
                    stats_date = date_from

                    stats_list.append((stats_date, item_id, stats_entry))

                return stats_list
            else:
                raise Exception('Invalid response format from Avito')
        else:
            raise Exception(f"Failed to retrieve data from Avito. Status code: {response.status_code}")

    def get(self, request, user_id, account_id):
        """
        Метод получения информации по аккаунту
        """
        try:
            account = Account.objects.get(user_id=user_id, account_id=account_id)
            serializer = AccountSerializer(account)
            response_data = {
                'success': True,
                'account': serializer.data
            }
            return Response(response_data)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id, account_id):
        """
        Метод удаления аккаунта
        """
        try:
            account = Account.objects.get(user_id=user_id, account_id=account_id)
            account.delete()
            return Response({"success": True, "deletedAccount": {"account_id": account_id}}, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

    def get_account_user_id(self, access_token):
        """
        Метод получения ID аккаунта от Avito
        """
        url = "https://api.avito.ru/core/v1/accounts/self"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                account_user_id = response.json().get("id")
                return account_user_id, None
            else:
                return None, f"Error: Unable to retrieve account_user_id. Status code: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return None, f"An error occurred: {e}"
