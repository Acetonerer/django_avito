from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from rights.models import UserRights
from rights.serializers import UserRightsSerializer


class RightsView(APIView):

    def post(self, request):
        try:
            serializer = UserRightsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({"success": True}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise APIException(detail=str(e))

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
