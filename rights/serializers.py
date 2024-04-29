from rest_framework import serializers
from .models import UserRights


class UserRightsSerializer(serializers.ModelSerializer):
    user_crm_id = serializers.CharField(max_length=100, source='id')
    rights = serializers.CharField(max_length=20)

    class Meta:
        model = UserRights
        fields = ['user_crm_id', 'rights']

    def to_internal_value(self, data):
        internal_data = []
        user_id = data.get('user_id')
        users = data.get('users')

        for user_crm_id, rights in users.items():
            internal_data.append({'id': user_crm_id, 'rights': rights, 'user': user_id})

        return internal_data
