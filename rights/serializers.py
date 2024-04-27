from rest_framework import serializers
from rights.models import UserRights


class UserRightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRights
        fields = ['user_crm_id', 'rights']
