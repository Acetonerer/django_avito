from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import make_aware
from ads.models import Ad
from ads.views import AdListView
from stats.models import Statistics
from .models import Account
from users.models import User
from .serializers import AccountSerializer
import requests
from account.token import get_access_token
from django.views.generic import TemplateView
from templates import *


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

            # Вызываем метод post из AdListView для получения и сохранения объявлений
            ad_view = AdListView()
            ad_response = ad_view.post(user_id=user_id, account_id=account.account_id)

            # Вызываем новый метод для получения статистики за каждый день прошлого месяца
            statistics_response = self.get_monthly_statistics(user_id=user_id, account_id=account.account_id)

            # Возвращаем успешный ответ
            return Response({'success': True, 'account_id': account.account_id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_monthly_statistics(self, user_id, account_id):
        try:
            account = get_object_or_404(Account, user_id=user_id, account_id=account_id)
            access_token = account.access_token

            ads = Ad.objects.filter(account_id=account_id)
            item_ids = [ad.ad_id for ad in ads]

            # Получаем дату начала и конца прошлого месяца
            today = datetime.now().date()
            one_month_ago = today - timedelta(days=30)  # За последние 30 дней
            date_from = one_month_ago.replace(day=1)  # Начало периода
            date_to = today - timedelta(days=1)  # Конец периода

            # Форматируем даты в строковый формат
            date_from_str = date_from.isoformat()
            date_to_str = date_to.isoformat()

            fields = ["uniqViews", "uniqContacts", "uniqFavorites"]
            period_grouping = "day"

            data = {
                "dateFrom": date_from_str,
                "dateTo": date_to_str,
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

            if response.status_code == 200:
                statistics_data = response.json()

                if 'result' in statistics_data and 'items' in statistics_data['result']:
                    items = statistics_data['result']['items']

                    for item in items:
                        item_id = item['itemId']
                        stats_list = item['stats']

                        for day in range(1, (today - one_month_ago).days + 1):
                            stats_date = one_month_ago + timedelta(days=day - 1)

                            # Ищем статистику для данного дня и объявления в списке
                            stats_entry = next(
                                (entry for entry in stats_list if entry['date'] == stats_date.isoformat()), None)

                            if stats_entry:
                                uniq_contacts = stats_entry.get('uniqContacts', 0)
                                uniq_favorites = stats_entry.get('uniqFavorites', 0)
                                uniq_views = stats_entry.get('uniqViews', 0)
                            else:
                                uniq_contacts = 0
                                uniq_favorites = 0
                                uniq_views = 0

                            # Проверяем существует ли запись для данного объявления и даты
                            stats_instance, created = Statistics.objects.get_or_create(
                                account=account,
                                date=stats_date,
                                ad_id=item_id,
                                defaults={
                                    'uniq_contacts': uniq_contacts,
                                    'uniq_favorites': uniq_favorites,
                                    'uniq_views': uniq_views
                                }
                            )

                            if not created:
                                # Если запись уже существует, обновляем значения
                                stats_instance.uniq_contacts = uniq_contacts
                                stats_instance.uniq_favorites = uniq_favorites
                                stats_instance.uniq_views = uniq_views
                                stats_instance.save()

                    return {'success': True, 'message': 'Statistics saved successfully.'}

                else:
                    return {'error': 'Invalid response format from Avito'}

            else:
                return {'error': f"Failed to retrieve data from Avito. Status code: {response.status_code}"}

        except Account.DoesNotExist:
            return {'error': 'Account not found'}
        except Exception as e:
            return {'error': f"An error occurred: {str(e)}"}

        except Account.DoesNotExist:
            return {'error': 'Account not found'}
        except Exception as e:
            return {'error': f"An error occurred: {str(e)}"}

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


class MainView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
