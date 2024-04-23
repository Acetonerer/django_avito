from django.urls import path
from .views import StatisticsView

urlpatterns = [
    path('stats/<user_id>/<account_id>/', StatisticsView.as_view(), name='stats'), # post
    path('stats/statistics', StatisticsView.as_view(), name='statistics'),
]
