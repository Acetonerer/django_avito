from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from account.models import Account
from .models import Ad
from .serializers import AdSerializer


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
                    """Пересоздание токена"""
                    refreshed_token, refresh_error = self.refresh_token(account.client_id, account.client_secret,
                                                                        account.refresh_token)
                    if refresh_error:
                        return Response({'error': refresh_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    headers['Authorization'] = f"Bearer {refreshed_token}"
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        items = response.json()
                        return Response({'success': True, 'items': items})
                    else:
                        return Response({
                            'error': f"Failed to refresh token and retrieve data from Avito."
                                     f" Status code: {response.status_code}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response(
                        {'error': f"Failed to retrieve data from Avito. Status code: {response.status_code}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except requests.exceptions.RequestException as e:
                return Response({'error': f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
