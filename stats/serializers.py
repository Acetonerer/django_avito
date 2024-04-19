from rest_framework import serializers
from .models import Statistics


class AdStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = ['ad_id', 'uniqContacts', 'uniqFavorites', 'uniqViews']


class DailyStatisticsSerializer(serializers.Serializer):
    date = serializers.DateField()
    ads = AdStatisticsSerializer(many=True)
