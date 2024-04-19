from django.urls import path
from .views import StatisticsView

urlpatterns = [
    path('stats/<user_id>/<account_id>/items', StatisticsView.as_view(), name='stats'),
    path('stats/statistics', StatisticsView.as_view(), name='statistics'),
]
