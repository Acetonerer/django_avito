from django.urls import path
from .views import AdListView

urlpatterns = [
    path("deps/<user_id>/<account_id>/", AdListView.as_view(), name="ads-list"),
]
