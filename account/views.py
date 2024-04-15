from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Account
from users.models import User
from .serializers import AccountSerializer
import requests
from ads.views import AdListView


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

        access_token, error = self.get_access_token(client_id, client_secret)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        refresh_token, error = self.get_refresh_token(client_id, client_secret, access_token)
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
                refresh_token=refresh_token,
            )
            serializer = AccountSerializer(account)
            response_data = {
                'success': True,
                'account': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

    def get_refresh_token(self, client_id, client_secret, refresh_token):
        """
        Метод обновления токена доступа Avito
        """
        url = "https://api.avito.ru/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                access_token = response.json().get("access_token")
                refresh_token = response.json().get("refresh_token")
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }, None
            else:
                return None, f"Error: Unable to refresh token. Status code: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return None, f"An error occurred: {e}"

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
