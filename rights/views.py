from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rights.models import UserRights


class RightsView(APIView):
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            users_data = request.data.get('users', {})

            # Проверка наличия обязательного поля "user_id"
            if not user_id:
                raise ValidationError("User ID is required")

            # Проверка наличия данных о пользователях
            if not users_data:
                raise ValidationError("Users data is required")

            # Цикл по данным о пользователях
            for user_crm_id, rights in users_data.items():
                UserRights.objects.create(user_id=user_id, user_crm_id=user_crm_id, rights=rights)

            return Response({'success': True}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        # Получаем объекты UserRights для указанного пользователя
        user_rights = UserRights.objects.filter(user_id=user_id)

        if user_rights:
            # Создаем словарь с правами пользователей
            rights_data = {}
            for user_right in user_rights:
                rights_data[f"{user_right.user_crm_id}"] = user_right.rights

            return Response({"rights": rights_data})
        else:
            return Response({"error": "User rights not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, user_id):
        # Получаем данные о пользователях из запроса
        users_data = request.data

        try:
            # Обновляем существующих пользователей
            for user_crm_id, rights in users_data.items():
                UserRights.objects.filter(user_id=user_id, user_crm_id=user_crm_id).update(rights=rights)

            # Добавляем новых пользователей, если их еще нет в базе данных
            new_users_data = [{**data, 'user_id': user_id} for data in users_data.items()]
            UserRights.objects.bulk_create([UserRights(**data) for data in new_users_data])

            return Response({"success": True})
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
