from django.urls import path
from .views import AdListView

urlpatterns = [
    path('accounts/<user_id>/<account_id>/ads', AdListView.as_view(), name='ad-list'),
]
