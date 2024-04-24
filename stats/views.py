from datetime import timedelta, datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
import requests
from account.models import Account
from rest_framework.response import Response
from django.utils import timezone

from account.token import get_new_access_token
from ads.models import Ad
from stats.models import Statistics


class StatisticsView(APIView):

    def post(self, user_id, account_id):
        try:
            account = get_object_or_404(Account, user_id=user_id, account_id=account_id)
            access_token = account.access_token

            ads = Ad.objects.filter(account_id=account_id)
            item_ids = [ad.ad_id for ad in ads]

            date_from = (timezone.now() - timedelta(days=1)).date()
            date_to = date_from

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
                        stats_date = date_from

                        if stats_list:
                            # Берем первую запись из stats_list
                            stats_entry = stats_list[0]
                            uniq_contacts = stats_entry.get('uniqContacts', 0)
                            uniq_favorites = stats_entry.get('uniqFavorites', 0)
                            uniq_views = stats_entry.get('uniqViews', 0)
                        else:
                            # Если stats_list пуст, устанавливаем значения по умолчанию
                            uniq_contacts, uniq_favorites, uniq_views = 0, 0, 0

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

                    return Response({'success': True, 'message': 'Statistics saved successfully.'})

                else:
                    return Response({'error': 'Invalid response format from Avito'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                return Response({'error': f"Failed to retrieve data from Avito. Status code: {response.status_code}"},
                                status=response.status_code)

        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):

        try:
            account_id = int(request.query_params.get('account_id'))
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            # Получаем статистику из базы данных
            statistics = Statistics.objects.filter(
                account_id=account_id,
                date__range=(start_date, end_date)
            )

            response_data = {'success': True, 'statistics': []}

            for stat in statistics:
                stat_date_str = stat.date.isoformat()
                stat_data = next((item for item in response_data['statistics'] if item['date'] == stat_date_str), None)

                if not stat_data:
                    stat_data = {'date': stat_date_str, 'ads': []}
                    response_data['statistics'].append(stat_data)

                stat_data['ads'].append({
                    'ad_id': stat.ad_id,
                    'uniqContacts': stat.uniq_contacts,
                    'uniqFavorites': stat.uniq_favorites,
                    'uniqViews': stat.uniq_views
                })

            # Получаем статистику от Avito за сегодняшний день
            today = timezone.now().date()
            account = get_object_or_404(Account, account_id=account_id)
            access_token = account.access_token
            client_id = account.client_id
            client_secret = account.client_secret

            ads = Ad.objects.filter(account_id=account_id)
            item_ids = [ad.ad_id for ad in ads]

            date_from = today
            date_to = today

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

            if response.status_code == 403:
                new_access_token, error = get_new_access_token(client_id, client_secret)

                if error:
                    return Response({'error': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Обновление токена в объекте account
                account.access_token = new_access_token
                account.save()

                url = f"https://api.avito.ru/stats/v1/accounts/{account.account_user_id}/items"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                response = requests.post(url, json=data, headers=headers)

            elif response.status_code == 200:

                statistics_data = response.json()

                if 'result' in statistics_data and 'items' in statistics_data['result']:
                    items = statistics_data['result']['items']

                    today_stats = {
                        'date': today.isoformat(),
                        'ads': []
                    }

                    for item in items:
                        item_id = item['itemId']
                        stats_list = item['stats']

                        if stats_list:
                            stats_entry = stats_list[0]
                            uniq_contacts = stats_entry.get('uniqContacts', 0)
                            uniq_favorites = stats_entry.get('uniqFavorites', 0)
                            uniq_views = stats_entry.get('uniqViews', 0)
                        else:
                            uniq_contacts, uniq_favorites, uniq_views = 0, 0, 0

                        today_stats['ads'].append({
                            'ad_id': item_id,
                            'uniqContacts': uniq_contacts,
                            'uniqFavorites': uniq_favorites,
                            'uniqViews': uniq_views
                        })

                    response_data['statistics'].append(today_stats)
                else:
                    return Response({'error': 'Invalid response format from Avito'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'error': f"Failed to retrieve Avito statistics. Status code: {response.status_code}"},
                                status=response.status_code)

            return Response(response_data)

        except ValueError as ve:
            return Response({'error': f"Invalid date format: {str(ve)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
