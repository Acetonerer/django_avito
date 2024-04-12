from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_id', 'client_id', 'client_secret', 'account_name', 'user_id', 'access_token',
                  'account_user_id']
