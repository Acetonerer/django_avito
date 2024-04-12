from django.urls import path
from .views import AdListView, AdStatisticsView

urlpatterns = [
    path('accounts/<user_id>/<account_id>/ads', AdListView.as_view(), name='ad-list'),
    path('accounts/<user_id>/<account_id>/items', AdStatisticsView.as_view(), name='post_stats-list'),
]
