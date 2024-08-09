from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from account.models import Account
from account.serializers import AccountSerializer
from .models import User


class UserDetailView(APIView):
    def get(self, request, user_id):
        """
        Получение данных по пользователю (аккаунтов, которые к нему привязаны)
        """
        try:
            user = get_object_or_404(User, user_id=user_id)
            accounts = Account.objects.filter(user_id=user_id)
            serializer = AccountSerializer(accounts, many=True)

            response_data = {
                "user_id": user.user_id,
                "accounts": serializer.data,
            }
            return Response(response_data)
        except Http404:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        """
        Метод создания пользователя
        """
        user_id = request.data.get("user_id")  # Получаем user_id из тела запроса
        if user_id is not None:
            try:
                user = User.objects.create_user(user_id)
                return Response({"success": True}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"success": False, "error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"success": False, "error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, user_id):
        """
        Метод удаления пользователя
        """
        try:
            user = User.objects.get(user_id=user_id)

            accounts = Account.objects.filter(user_id=user_id)
            accounts.delete()

            user.delete()
            return Response(
                {"success": True, "deletedUser": {"deletedUserId": user_id}},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
