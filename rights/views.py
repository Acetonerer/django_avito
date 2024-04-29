from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rights.models import UserRights
from rights.serializers import UserRightsSerializer


class RightsView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        users_data = request.data.get('users', {
            'user_crm_id': 'rights'
        })

        # Проверка наличия обязательного поля "user_id"
        if not user_id:
            raise ValidationError("User ID is required")

        # Проверка наличия данных о пользователях
        if not users_data:
            raise ValidationError("Users data is required")

        # Цикл по данным о пользователях
        for user_crm_id, rights in users_data.items():
            UserRights.objects.create(user=request.user, user_crm_id=user_crm_id, rights=rights)

        return Response({"success": True}, status=status.HTTP_201_CREATED)

    def get(self, request, user_id):
        user_rights = UserRights.objects.filter(user=request.user, user_crm_id=user_id).first()
        if user_rights:
            serializer = UserRightsSerializer(user_rights)
            return Response(serializer.data)
        return Response({"error": "User rights not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        user_rights = UserRights.objects.filter(user=request.user, user_crm_id=user_id).first()
        if user_rights:
            serializer = UserRightsSerializer(user_rights, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": True})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "User rights not found"}, status=status.HTTP_404_NOT_FOUND)
