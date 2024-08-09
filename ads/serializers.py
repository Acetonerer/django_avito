from rest_framework import serializers
from .models import Ad


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ["id", "title", "status", "account_id"]
